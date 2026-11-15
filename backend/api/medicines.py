from fastapi import APIRouter, HTTPException
from database.supabase_client import get_db
from models.schemas import MedicineUpdateRequest, MedicineResponse
from services.medicine_normalization import normalize_medicine_name

router = APIRouter(prefix="/medicines", tags=["Medicines Management"])

@router.put("/{id}", response_model=MedicineResponse)
def update_medicine(id: str, payload: MedicineUpdateRequest):
    """
    Allows patient or caregiver to correct an extracted medicine name, strength, dosage,
    or frequency before final clinical consolidation.
    """
    db = get_db()
    res = db.table("medicines").select("*").eq("id", id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Medicine record not found")

    existing = res.data[0]
    update_data = {}

    if payload.original_name is not None:
        update_data["original_name"] = payload.original_name
        # Re-normalize with updated name
        norm = normalize_medicine_name(payload.original_name)
        update_data["normalized_name"] = norm.get("generic_name")
        update_data["generic_name"] = norm.get("generic_name")
        update_data["active_ingredient"] = norm.get("active_ingredient")
    
    if payload.strength is not None:
        update_data["strength"] = payload.strength
    if payload.dosage is not None:
        update_data["dosage"] = payload.dosage
    if payload.frequency is not None:
        update_data["frequency"] = payload.frequency
    if payload.duration is not None:
        update_data["duration"] = payload.duration
    if payload.instructions is not None:
        update_data["instructions"] = payload.instructions
    if payload.requires_verification is not None:
        update_data["requires_verification"] = payload.requires_verification

    update_res = db.table("medicines").update(update_data).eq("id", id).execute()
    rows = update_res.data if isinstance(update_res.data, list) else []
    row: dict = rows[0] if rows and isinstance(rows[0], dict) else {**existing, **update_data}
    
    return MedicineResponse(
        id=str(row.get("id", id)),
        prescription_id=str(row.get("prescription_id", "")),
        user_id=str(row.get("user_id", "")),
        original_name=str(row.get("original_name", "")),
        normalized_name=row.get("normalized_name"),
        generic_name=row.get("generic_name"),
        active_ingredient=row.get("active_ingredient"),
        strength=row.get("strength"),
        dosage=row.get("dosage"),
        frequency=row.get("frequency"),
        duration=row.get("duration"),
        route=str(row.get("route", "oral")),
        instructions=row.get("instructions"),
        confidence=float(row.get("confidence", 1.0) or 1.0),
        requires_verification=bool(row.get("requires_verification", False)),
        created_at=row.get("created_at")
    )

@router.delete("/{id}")
def delete_medicine(id: str):
    """
    Removes an incorrectly extracted medicine line item.
    """
    db = get_db()
    db.table("medicines").delete().eq("id", id).execute()
    return {"message": "Medicine removed successfully", "id": id}
