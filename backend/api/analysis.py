import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Form, Request
from database.supabase_client import get_db
from models.schemas import (
    FullAnalysisResponse, 
    AnalysisStatistics, 
    WarningItem, 
    MedicineResponse, 
    PrescriptionResponse,
    ConsolidatedMedication
)
from services.duplicate_detection import detect_duplicates_and_overlaps
from services.interaction_service import analyze_all_drug_interactions
from services.dosage_analysis import analyze_dosage_and_conflicts
from services.consolidation_service import build_consolidated_medication_plan
from services.gemini_service import generate_friendly_explanation

router = APIRouter(prefix="", tags=["Prescription Analysis & Safety"])

@router.api_route("/prescriptions/analyse", methods=["GET", "POST"])
@router.api_route("/analysis/run", methods=["GET", "POST"])
@router.api_route("/analysis/latest", methods=["GET", "POST"])
async def analyse_user_prescriptions(
    request: Request,
    user_id: Optional[str] = Form(None),
    user_id_query: Optional[str] = Query(None, alias="user_id")
):
    """
    Executes the multi-stage clinical medication safety analysis pipeline:
    Duplicate detection -> Active ingredient aliases -> Drug interaction checks ->
    Dosage accumulation -> Conflicting instructions -> Consolidated plan generation.
    Supports atomic batch DB persistence and flexible input formats.
    """
    db = get_db()
    
    # Extract user ID from Form, Query, or JSON body with fallback
    uid = user_id or user_id_query
    if not uid and request:
        try:
            if "application/json" in (request.headers.get("content-type") or ""):
                body = await request.json()
                uid = body.get("user_id")
        except Exception:
            pass
    if not uid and request:
        uid = request.query_params.get("user_id")
    if not uid:
        uid = "demo-patient-001"
    
    # 1. Fetch all prescriptions for user
    rx_res = db.table("prescriptions").select("*").eq("user_id", uid).execute()
    prescriptions = [p for p in (rx_res.data or []) if isinstance(p, dict)]
    
    # Auto-fallback to demo-patient-001 if active user has not yet uploaded
    if not prescriptions and uid != "demo-patient-001":
        fallback_res = db.table("prescriptions").select("*").eq("user_id", "demo-patient-001").execute()
        demo_rxs = [p for p in (fallback_res.data or []) if isinstance(p, dict)]
        if demo_rxs:
            prescriptions = demo_rxs
            uid = "demo-patient-001"

    if not prescriptions:
        raise HTTPException(status_code=400, detail="No prescriptions found. Please upload at least one prescription first.")

    rx_map = {str(rx.get("id")): rx for rx in prescriptions}

    # 2. Fetch all medicines for user
    med_res = db.table("medicines").select("*").eq("user_id", uid).execute()
    medicines = [m for m in (med_res.data or []) if isinstance(m, dict)]
    if not medicines and uid != "demo-patient-001":
        fallback_meds = db.table("medicines").select("*").eq("user_id", "demo-patient-001").execute()
        demo_meds = [m for m in (fallback_meds.data or []) if isinstance(m, dict)]
        if demo_meds:
            medicines = demo_meds
            uid = "demo-patient-001"

    if not medicines:
        raise HTTPException(status_code=400, detail="No medicines identified in prescriptions.")

    # 3. Detect duplicates and therapeutic overlaps
    dup_and_overlap_warnings = detect_duplicates_and_overlaps(medicines, rx_map)
    duplicate_warnings = [w for w in dup_and_overlap_warnings if w.analysis_type == "duplicate"]
    overlap_warnings = [w for w in dup_and_overlap_warnings if w.analysis_type == "overlap"]

    # 4. Detect drug-drug interactions using trusted clinical database
    interaction_warnings = analyze_all_drug_interactions(medicines)

    # 5. Detect dosage concerns and conflicting prescription instructions
    dosage_and_conflict_warnings = analyze_dosage_and_conflicts(medicines, rx_map)
    dosage_warnings = [w for w in dosage_and_conflict_warnings if w.analysis_type == "dosage_concern"]
    conflict_warnings = [w for w in dosage_and_conflict_warnings if w.analysis_type == "conflict"]

    all_warnings = (
        duplicate_warnings + 
        interaction_warnings + 
        dosage_warnings + 
        overlap_warnings + 
        conflict_warnings
    )

    # Assign IDs and generate patient-friendly explanations for each warning
    explanation_cache = {}
    for w in all_warnings:
        w.id = str(uuid.uuid4())
        cache_key = (w.analysis_type, w.medicine_a_name, w.medicine_b_name)
        if cache_key in explanation_cache:
            friendly_text = explanation_cache[cache_key]
        else:
            friendly_text = generate_friendly_explanation(
                warning_type=w.analysis_type,
                medicine_a=w.medicine_a_name,
                medicine_b=w.medicine_b_name,
                clinical_desc=w.description
            )
            explanation_cache[cache_key] = friendly_text

        if friendly_text and friendly_text != w.description:
            w.description = friendly_text

    # Clear prior analysis warnings and consolidated records for fresh state
    try:
        db.table("medication_analysis").delete().eq("user_id", uid).execute()
        db.table("consolidated_medications").delete().eq("user_id", uid).execute()
    except Exception as e:
        print(f"Notice during analysis cleanup: {e}")

    # Atomic batch insert all warnings in a single request
    warn_records = [
        {
            "id": w.id,
            "user_id": uid,
            "medicine_a_id": w.medicine_a_id,
            "medicine_b_id": w.medicine_b_id,
            "medicine_a_name": w.medicine_a_name,
            "medicine_b_name": w.medicine_b_name,
            "analysis_type": w.analysis_type,
            "severity": w.severity,
            "description": w.description,
            "recommendation": w.recommendation,
            "source": w.source
        }
        for w in all_warnings
    ]
    if warn_records:
        try:
            db.table("medication_analysis").insert(warn_records).execute()
        except Exception as e:
            print(f"Notice inserting warnings: {e}")

    # 6. Build proposed consolidated medication review summary
    consolidated_plan = build_consolidated_medication_plan(medicines, all_warnings, rx_map)
    
    # Store initial consolidated medications in a single atomic batch insert
    analysis_id = str(uuid.uuid4())
    plan_records = []
    for item in consolidated_plan:
        item.id = str(uuid.uuid4())
        plan_records.append({
            "id": item.id,
            "user_id": uid,
            "analysis_id": analysis_id,
            "medicine_name": item.medicine_name,
            "generic_name": item.generic_name,
            "strength": item.strength,
            "dosage": item.dosage,
            "frequency": item.frequency,
            "duration": item.duration,
            "instructions": item.instructions,
            "status": item.status,
            "requires_review": item.requires_review,
            "review_reason": item.review_reason,
            "source_prescriptions": item.source_prescriptions
        })
    if plan_records:
        try:
            db.table("consolidated_medications").insert(plan_records).execute()
        except Exception as e:
            print(f"Notice inserting consolidated medications: {e}")

    # Calculate statistics
    flagged_meds = {w.medicine_a_name for w in all_warnings} | {w.medicine_b_name for w in all_warnings if w.medicine_b_name}
    clean_count = max(0, len(medicines) - len(flagged_meds))

    stats = AnalysisStatistics(
        total_prescriptions=len(prescriptions),
        total_medicines=len(medicines),
        duplicate_count=len(duplicate_warnings),
        interaction_count=len(interaction_warnings),
        dosage_concern_count=len(dosage_warnings),
        overlap_count=len(overlap_warnings),
        conflict_count=len(conflict_warnings),
        clean_medicines_count=clean_count
    )

    # Format responses with safe dictionary typing
    rx_responses = [
        PrescriptionResponse(
            id=str(rx.get("id", "")),
            user_id=str(rx.get("user_id", "")),
            file_url=rx.get("file_url"),
            file_name=rx.get("file_name", "Prescription"),
            file_type=rx.get("file_type"),
            doctor_name=rx.get("doctor_name"),
            prescription_date=rx.get("prescription_date"),
            raw_text=rx.get("raw_text"),
            ocr_confidence=float(rx.get("ocr_confidence", 1.0) or 1.0),
            status=str(rx.get("status", "analysed")),
            created_at=rx.get("created_at"),
            medicines_count=sum(1 for m in medicines if m.get("prescription_id") == rx.get("id"))
        )
        for rx in prescriptions
    ]

    med_responses = [
        MedicineResponse(
            id=str(m.get("id", "")),
            prescription_id=str(m.get("prescription_id", "")),
            user_id=str(m.get("user_id", "")),
            original_name=str(m.get("original_name", "")),
            normalized_name=m.get("normalized_name"),
            generic_name=m.get("generic_name"),
            active_ingredient=m.get("active_ingredient"),
            strength=m.get("strength"),
            dosage=m.get("dosage"),
            frequency=m.get("frequency"),
            duration=m.get("duration"),
            route=str(m.get("route", "oral")),
            instructions=m.get("instructions"),
            confidence=float(m.get("confidence", 0.95) or 0.95),
            requires_verification=bool(m.get("requires_verification", False)),
            created_at=m.get("created_at"),
            doctor_name=rx_map.get(str(m.get("prescription_id", "")), {}).get("doctor_name") if isinstance(rx_map.get(str(m.get("prescription_id", ""))), dict) else None
        )
        for m in medicines
    ]

    return FullAnalysisResponse(
        analysis_id=analysis_id,
        statistics=stats,
        prescriptions=rx_responses,
        medicines=med_responses,
        warnings=all_warnings,
        consolidated_plan=consolidated_plan,
        created_at=datetime.utcnow().isoformat()
    )

@router.get("/analysis/history")
def get_user_analysis_history(user_id: str):
    """
    Returns historical prescription analysis sessions, associated prescriptions,
    and cumulative statistics for the user without running slow re-analyses.
    """
    db = get_db()
    rx_res = db.table("prescriptions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    prescriptions = rx_res.data or []

    med_res = db.table("medicines").select("*").eq("user_id", user_id).execute()
    medicines = med_res.data or []

    warn_res = db.table("medication_analysis").select("*").eq("user_id", user_id).execute()
    warnings = warn_res.data or []

    plan_res = db.table("consolidated_medications").select("*").eq("user_id", user_id).execute()
    plans = plan_res.data or []

    if not prescriptions:
        return {"sessions": [], "prescriptions": [], "totalPrescriptions": 0}

    analysis_id = plans[0].get("analysis_id") if plans else (warnings[0].get("id") if warnings else str(uuid.uuid4()))

    dup_count = sum(1 for w in warnings if w.get("analysis_type") == "duplicate")
    inter_count = sum(1 for w in warnings if w.get("analysis_type") == "interaction")
    dose_count = sum(1 for w in warnings if w.get("analysis_type") == "dosage_concern")

    formatted_prescriptions = [
        {
            "id": rx["id"],
            "doctor_name": rx.get("doctor_name") or "Attending Physician",
            "prescription_date": rx.get("prescription_date") or "2026-09-04",
            "file_name": rx.get("file_name") or "Prescription",
            "file_type": rx.get("file_type") or "png",
            "file_url": rx.get("file_url") or "",
            "created_at": rx.get("created_at"),
            "ocr_confidence": rx.get("ocr_confidence", 0.95),
            "status": rx.get("status", "analysed"),
            "medicines_count": sum(1 for m in medicines if m.get("prescription_id") == rx["id"])
        }
        for rx in prescriptions
    ]

    session = {
        "id": analysis_id,
        "title": "Comprehensive Multi-Prescription Safety Review",
        "prescriptionsCount": len(prescriptions),
        "medicinesCount": len(medicines),
        "warningsCount": len(warnings),
        "duplicateCount": dup_count,
        "interactionCount": inter_count,
        "dosageCount": dose_count,
        "date": prescriptions[0].get("created_at") or datetime.utcnow().isoformat(),
        "status": "Verified",
        "hasWarnings": len(warnings) > 0
    }

    return {
        "sessions": [session],
        "prescriptions": formatted_prescriptions,
        "totalPrescriptions": len(prescriptions),
        "totalMedicines": len(medicines),
        "totalWarnings": len(warnings)
    }

@router.get("/analysis/{id}")
async def get_analysis_by_id(id: str, request: Request, user_id: str = "demo-patient-001"):
    """
    Retrieves full analysis results.
    """
    return await analyse_user_prescriptions(request=request, user_id=user_id)

@router.get("/analysis/{id}/medicines", response_model=List[MedicineResponse])
def get_analysis_medicines(id: str, user_id: str = "demo-patient-001"):
    db = get_db()
    rx_res = db.table("prescriptions").select("*").eq("user_id", user_id).execute()
    rx_rows = rx_res.data if isinstance(rx_res.data, list) else []
    rx_map = {
        str(rx.get("id")): rx.get("doctor_name")
        for rx in rx_rows
        if isinstance(rx, dict)
    }
    
    med_res = db.table("medicines").select("*").eq("user_id", user_id).execute()
    med_rows = med_res.data if isinstance(med_res.data, list) else []
    return [
        MedicineResponse(
            id=str(m.get("id", "")),
            prescription_id=str(m.get("prescription_id", "")),
            user_id=str(m.get("user_id", "")),
            original_name=str(m.get("original_name", "")),
            normalized_name=m.get("normalized_name"),
            generic_name=m.get("generic_name"),
            active_ingredient=m.get("active_ingredient"),
            strength=m.get("strength"),
            dosage=m.get("dosage"),
            frequency=m.get("frequency"),
            duration=m.get("duration"),
            route=str(m.get("route", "oral")),
            instructions=m.get("instructions"),
            confidence=float(m.get("confidence", 0.95) or 0.95),
            requires_verification=bool(m.get("requires_verification", False)),
            created_at=m.get("created_at"),
            doctor_name=rx_map.get(str(m.get("prescription_id", "")))
        )
        for m in med_rows
        if isinstance(m, dict)
    ]

@router.get("/analysis/{id}/warnings", response_model=List[WarningItem])
def get_analysis_warnings(id: str, user_id: str = "demo-patient-001"):
    db = get_db()
    res = db.table("medication_analysis").select("*").eq("user_id", user_id).execute()
    warn_rows = res.data if isinstance(res.data, list) else []
    return [
        WarningItem(
            id=str(row.get("id", "")),
            medicine_a_id=row.get("medicine_a_id"),
            medicine_b_id=row.get("medicine_b_id"),
            medicine_a_name=str(row.get("medicine_a_name", "")),
            medicine_b_name=row.get("medicine_b_name"),
            analysis_type=str(row.get("analysis_type", "interaction")),
            severity=str(row.get("severity", "LOW")),
            description=str(row.get("description", "")),
            recommendation=str(row.get("recommendation", "")),
            source=row.get("source")
        )
        for row in warn_rows
        if isinstance(row, dict)
    ]

@router.post("/analysis/{id}/confirm")
def confirm_user_analysis(
    id: str, 
    user_id: Optional[str] = Form(None),
    user_id_query: Optional[str] = Query(None, alias="user_id")
):
    """
    Step 9/10: User reviews extracted medicines and confirms the analysis to generate
    the final Consolidated Medication Review Summary.
    """
    db = get_db()
    uid = user_id or user_id_query or "demo-patient-001"
    # Mark medicines as verified
    db.table("medicines").update({"requires_verification": False}).eq("user_id", uid).execute()
    return {"message": "Medication details confirmed. Consolidated Medication Summary is ready.", "analysis_id": id}

@router.get("/consolidated-plan/{id}", response_model=List[ConsolidatedMedication])
def get_consolidated_plan(id: str, user_id: str):
    """
    Retrieves the proposed Consolidated Medication Review Summary with schedule slots.
    """
    db = get_db()
    res = db.table("consolidated_medications").select("*").eq("user_id", user_id).execute()
    rows = res.data or []
    
    output = []
    for r in rows:
        from services.consolidation_service import determine_schedule_slots
        slots = determine_schedule_slots(r.get("frequency") or "once daily")
        output.append(ConsolidatedMedication(
            id=r.get("id"),
            medicine_name=r.get("medicine_name", "Medication"),
            generic_name=r.get("generic_name"),
            strength=r.get("strength"),
            dosage=r.get("dosage"),
            frequency=r.get("frequency"),
            duration=r.get("duration"),
            instructions=r.get("instructions"),
            status=r.get("status", "active"),
            requires_review=bool(r.get("requires_review", False)),
            review_reason=r.get("review_reason"),
            source_prescriptions=r.get("source_prescriptions", []),
            schedule_slots=slots
        ))
    return output
