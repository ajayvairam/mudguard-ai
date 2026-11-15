from typing import Optional
from fastapi import APIRouter, HTTPException, Response, Form, Query, Request
from database.supabase_client import get_db
from services.pdf_service import generate_medication_summary_pdf
from api.analysis import analyse_user_prescriptions

router = APIRouter(prefix="", tags=["PDF Generation"])

@router.post("/consolidated-plan/{id}/pdf")
async def export_consolidated_plan_pdf(
    id: str, 
    request: Request,
    user_id: Optional[str] = Form(None),
    user_id_query: Optional[str] = Query(None, alias="user_id")
):
    """
    Generates and returns the official Consolidated Medication Summary PDF matching Section 27.
    """
    db = get_db()
    uid = user_id or user_id_query or "demo-patient-001"
    
    # Get user profile for patient name
    prof_res = db.table("profiles").select("*").eq("user_id", uid).execute()
    patient_name = "Patient"
    if prof_res.data:
        patient_name = prof_res.data[0].get("full_name") or "Patient"

    # Fetch full analysis data
    try:
        full_analysis = await analyse_user_prescriptions(request=request, user_id=uid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot generate PDF: {str(e)}")

    pdf_bytes = generate_medication_summary_pdf(full_analysis.model_dump(), patient_name=patient_name)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=MediGuard_Medication_Summary_{id[:8]}.pdf"
        }
    )
