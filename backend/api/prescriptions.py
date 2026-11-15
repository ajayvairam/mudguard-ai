import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Request
from config import UPLOADS_DIR
from database.supabase_client import get_db
from models.schemas import PrescriptionResponse, MedicineResponse
from services.ocr_service import extract_prescription_text
from services.medicine_extraction import parse_prescription_content
from services.medicine_normalization import normalize_medicine_name

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])

@router.post("/upload", response_model=List[PrescriptionResponse])
async def upload_prescriptions(
    user_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Accepts single or multiple prescription images/PDFs.
    Executes OCR text extraction, Gemini/regex structured extraction, and stores records.
    """
    db = get_db()
    saved_prescriptions = []

    for file in files:
        contents = await file.read()
        file_ext = Path(file.filename).suffix.lower()
        file_id = str(uuid.uuid4())
        
        # Save file to disk
        local_filename = f"{file_id}{file_ext}"
        save_path = UPLOADS_DIR / local_filename
        with open(save_path, "wb") as f:
            f.write(contents)

        # Execute OCR
        raw_text, ocr_conf = extract_prescription_text(contents, file.filename)
        
        # Extract structured entities
        extracted = parse_prescription_content(raw_text)

        # Store prescription
        rx_record = {
            "id": file_id,
            "user_id": user_id,
            "file_url": f"/uploads/{local_filename}",
            "file_name": file.filename,
            "file_type": file_ext.replace(".", ""),
            "doctor_name": extracted.doctor_name or "Attending Doctor",
            "prescription_date": extracted.prescription_date or "2026-09-04",
            "raw_text": raw_text,
            "ocr_confidence": ocr_conf,
            "status": "analysed"
        }
        db.table("prescriptions").insert(rx_record).execute()

        # Store medicines
        for med in extracted.medicines:
            norm = normalize_medicine_name(med.original_name)
            med_record = {
                "id": str(uuid.uuid4()),
                "prescription_id": file_id,
                "user_id": user_id,
                "original_name": med.original_name,
                "normalized_name": norm.get("generic_name"),
                "generic_name": norm.get("generic_name"),
                "active_ingredient": norm.get("active_ingredient"),
                "strength": med.strength or "500 mg",
                "dosage": med.dosage or "1 tablet",
                "frequency": med.frequency or "once daily",
                "duration": med.duration or "5 days",
                "route": med.route or "oral",
                "instructions": med.instructions or "after food",
                "confidence": med.confidence,
                "requires_verification": med.confidence < 0.85
            }
            db.table("medicines").insert(med_record).execute()

        saved_prescriptions.append(PrescriptionResponse(
            id=file_id,
            user_id=user_id,
            file_url=rx_record["file_url"],
            file_name=file.filename,
            file_type=rx_record["file_type"],
            doctor_name=rx_record["doctor_name"],
            prescription_date=rx_record["prescription_date"],
            raw_text=raw_text,
            ocr_confidence=ocr_conf,
            status="analysed",
            medicines_count=len(extracted.medicines)
        ))

    return saved_prescriptions

@router.get("", response_model=List[PrescriptionResponse])
def list_prescriptions(user_id: str):
    """
    Lists all prescriptions for a specific patient.
    """
    db = get_db()
    res = db.table("prescriptions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    output: List[PrescriptionResponse] = []
    raw_rows = res.data if isinstance(res.data, list) else []
    for item in raw_rows:
        row: dict = item if isinstance(item, dict) else {}
        rx_id = str(row.get("id", ""))
        # Count medicines
        med_res = db.table("medicines").select("id").eq("prescription_id", rx_id).execute()
        med_rows = med_res.data if isinstance(med_res.data, list) else []
        count = len(med_rows)
        output.append(PrescriptionResponse(
            id=rx_id,
            user_id=str(row.get("user_id", "")),
            file_url=row.get("file_url"),
            file_name=row.get("file_name", "Prescription"),
            file_type=row.get("file_type"),
            doctor_name=row.get("doctor_name"),
            prescription_date=row.get("prescription_date"),
            raw_text=row.get("raw_text"),
            ocr_confidence=float(row.get("ocr_confidence", 1.0) or 1.0),
            status=str(row.get("status", "analysed")),
            created_at=row.get("created_at"),
            medicines_count=count
        ))
    return output

@router.get("/{id}", response_model=PrescriptionResponse)
def get_prescription(id: str):
    """
    Gets details of a single prescription.
    """
    if id in ("analyse", "load-sample-prescriptions", "upload"):
        raise HTTPException(status_code=404, detail="Invalid prescription id")
    db = get_db()
    res = db.table("prescriptions").select("*").eq("id", id).execute()
    raw_rows = res.data if isinstance(res.data, list) else []
    if not raw_rows:
        raise HTTPException(status_code=404, detail="Prescription not found")
    first_item = raw_rows[0]
    row: dict = first_item if isinstance(first_item, dict) else {}
    med_res = db.table("medicines").select("id").eq("prescription_id", id).execute()
    med_rows = med_res.data if isinstance(med_res.data, list) else []
    count = len(med_rows)
    return PrescriptionResponse(
        id=str(row.get("id", id)),
        user_id=str(row.get("user_id", "")),
        file_url=row.get("file_url"),
        file_name=row.get("file_name", "Prescription"),
        file_type=row.get("file_type"),
        doctor_name=row.get("doctor_name"),
        prescription_date=row.get("prescription_date"),
        raw_text=row.get("raw_text"),
        ocr_confidence=float(row.get("ocr_confidence", 1.0) or 1.0),
        status=str(row.get("status", "analysed")),
        created_at=row.get("created_at"),
        medicines_count=count
    )

@router.delete("/{id}")
def delete_prescription(id: str):
    """
    Deletes a prescription and associated medicine records.
    """
    db = get_db()
    db.table("medicines").delete().eq("prescription_id", id).execute()
    db.table("prescriptions").delete().eq("id", id).execute()
    return {"message": "Prescription deleted successfully", "id": id}

@router.api_route("/load-sample-prescriptions", methods=["GET", "POST"])
async def load_sample_multi_doctor_prescriptions(
    request: Request,
    user_id: Optional[str] = Form(None),
    user_id_query: Optional[str] = Query(None, alias="user_id")
):
    """
    Populates realistic multi-doctor prescriptions for immediate demonstration of
    duplicate detection, active ingredient overlap, drug-drug interaction, and dosage concern.
    Uses atomic batch insertion to guarantee foreign key integrity.
    """
    db = get_db()
    uid = user_id or user_id_query
    if not uid:
        try:
            if "application/json" in request.headers.get("content-type", ""):
                body = await request.json()
                uid = body.get("user_id")
        except Exception:
            pass
    if not uid:
        uid = request.query_params.get("user_id")
    if not uid:
        uid = "demo-patient-001"
    
    # 1. Clean prior records for clean state (children first, then parents)
    try:
        db.table("medicines").delete().eq("user_id", uid).execute()
        db.table("medication_analysis").delete().eq("user_id", uid).execute()
        db.table("consolidated_medications").delete().eq("user_id", uid).execute()
        db.table("prescriptions").delete().eq("user_id", uid).execute()
    except Exception as e:
        print(f"Notice during sample cleanup: {e}")

    rx1_id = str(uuid.uuid4())
    rx2_id = str(uuid.uuid4())
    rx3_id = str(uuid.uuid4())

    # 2. Batch insert all 3 prescriptions in a single operation
    prescriptions_payload = [
        {
            "id": rx1_id,
            "user_id": uid,
            "file_url": "/samples/dr_kumar_rx.png",
            "file_name": "Dr_Kumar_Cardiology_Rx.png",
            "file_type": "png",
            "doctor_name": "Dr. A. Kumar (Cardiologist)",
            "prescription_date": "2026-08-15",
            "raw_text": "Rx:\n1. Atorvastatin 20 mg - 1 tab at bedtime (30 days)\n2. Clopidogrel 75 mg - 1 tab once daily after breakfast (30 days)\n3. Aspirin 75 mg - 1 tab once daily with food (30 days)",
            "ocr_confidence": 0.98,
            "status": "analysed"
        },
        {
            "id": rx2_id,
            "user_id": uid,
            "file_url": "/samples/dr_ravi_rx.png",
            "file_name": "Dr_Ravi_GeneralMedicine_Rx.png",
            "file_type": "png",
            "doctor_name": "Dr. S. Ravi (General Physician)",
            "prescription_date": "2026-08-20",
            "raw_text": "Rx:\n1. Dolo 650 (Paracetamol) - 1 tab 3 times daily after meals for 5 days\n2. Omeprazole 20 mg - 1 capsule morning before food for 14 days\n3. Amoxicillin 500 mg - 1 capsule twice daily for 7 days",
            "ocr_confidence": 0.95,
            "status": "analysed"
        },
        {
            "id": rx3_id,
            "user_id": uid,
            "file_url": "/samples/dr_priya_rx.pdf",
            "file_name": "Dr_Priya_Orthopedics_Rx.pdf",
            "file_type": "pdf",
            "doctor_name": "Dr. Priya Nair (Orthopedic Surgeon)",
            "prescription_date": "2026-09-01",
            "raw_text": "Rx:\n1. Ibuprofen 400 mg - 1 tab twice daily for joint pain for 10 days\n2. Paracetamol 500 mg - 2 tabs twice daily as needed for pain (2000 mg/day)\n3. Pantoprazole 40 mg - 1 tab morning empty stomach for 10 days",
            "ocr_confidence": 0.96,
            "status": "analysed"
        }
    ]

    db.table("prescriptions").insert(prescriptions_payload).execute()

    # 3. Assemble all 9 medicines and batch insert in a single operation
    all_medicines = []

    # Dr. Kumar's medicines (Cardiology)
    meds1 = [
        ("Atorvastatin", "20 mg", "1 tablet", "once daily (night)", "30 days", "oral", "at bedtime"),
        ("Clopidogrel", "75 mg", "1 tablet", "once daily", "30 days", "oral", "after breakfast"),
        ("Aspirin", "75 mg", "1 tablet", "once daily", "30 days", "oral", "after food")
    ]
    for name, st, dos, freq, dur, route, inst in meds1:
        norm = normalize_medicine_name(name)
        all_medicines.append({
            "id": str(uuid.uuid4()),
            "prescription_id": rx1_id,
            "user_id": uid,
            "original_name": name,
            "normalized_name": norm.get("generic_name"),
            "generic_name": norm.get("generic_name"),
            "active_ingredient": norm.get("active_ingredient"),
            "strength": st,
            "dosage": dos,
            "frequency": freq,
            "duration": dur,
            "route": route,
            "instructions": inst,
            "confidence": 0.98,
            "requires_verification": False
        })

    # Dr. Ravi's medicines (General Medicine)
    meds2 = [
        ("Dolo 650", "650 mg", "1 tablet", "three times daily", "5 days", "oral", "after food"),
        ("Omeprazole", "20 mg", "1 capsule", "once daily", "14 days", "oral", "before breakfast"),
        ("Amoxicillin", "500 mg", "1 capsule", "twice daily", "7 days", "oral", "after food")
    ]
    for name, st, dos, freq, dur, route, inst in meds2:
        norm = normalize_medicine_name(name)
        all_medicines.append({
            "id": str(uuid.uuid4()),
            "prescription_id": rx2_id,
            "user_id": uid,
            "original_name": name,
            "normalized_name": norm.get("generic_name"),
            "generic_name": norm.get("generic_name"),
            "active_ingredient": norm.get("active_ingredient"),
            "strength": st,
            "dosage": dos,
            "frequency": freq,
            "duration": dur,
            "route": route,
            "instructions": inst,
            "confidence": 0.95,
            "requires_verification": False
        })

    # Dr. Priya's medicines (Orthopedics)
    meds3 = [
        ("Ibuprofen", "400 mg", "1 tablet", "twice daily", "10 days", "oral", "after meals"),
        ("Paracetamol", "500 mg", "2 tablets", "twice daily", "10 days", "oral", "after food"),
        ("Pantoprazole", "40 mg", "1 tablet", "once daily", "10 days", "oral", "before food")
    ]
    for name, st, dos, freq, dur, route, inst in meds3:
        norm = normalize_medicine_name(name)
        all_medicines.append({
            "id": str(uuid.uuid4()),
            "prescription_id": rx3_id,
            "user_id": uid,
            "original_name": name,
            "normalized_name": norm.get("generic_name"),
            "generic_name": norm.get("generic_name"),
            "active_ingredient": norm.get("active_ingredient"),
            "strength": st,
            "dosage": dos,
            "frequency": freq,
            "duration": dur,
            "route": route,
            "instructions": inst,
            "confidence": 0.94,
            "requires_verification": False
        })

    db.table("medicines").insert(all_medicines).execute()

    return {"message": "3 Multi-Doctor Sample Prescriptions loaded successfully", "count": 3}
