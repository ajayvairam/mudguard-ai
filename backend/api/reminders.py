import uuid
from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Form
from database.supabase_client import get_db
from models.schemas import (
    ReminderCreateRequest, 
    ReminderResponse, 
    ReminderHistoryItem
)

router = APIRouter(prefix="/reminders", tags=["Medication Reminders"])

@router.post("", response_model=ReminderResponse)
def create_reminder(
    payload: ReminderCreateRequest, 
    user_id: Optional[str] = Query(None)
):
    """
    Schedules a new medication reminder.
    """
    db = get_db()
    rem_id = str(uuid.uuid4())
    today_str = date.today().isoformat()
    uid = user_id or getattr(payload, "user_id", None) or "demo-patient-001"
    
    record = {
        "id": rem_id,
        "user_id": uid,
        "medicine_id": payload.medicine_id,
        "medicine_name": payload.medicine_name,
        "dose": payload.dose,
        "time": payload.time,
        "frequency": payload.frequency,
        "start_date": payload.start_date or today_str,
        "end_date": payload.end_date,
        "instructions": payload.instructions or "Take with a glass of water",
        "enabled": True
    }
    db.table("reminders").insert(record).execute()

    return ReminderResponse(
        id=rem_id,
        user_id=uid,
        medicine_id=payload.medicine_id,
        medicine_name=payload.medicine_name,
        dose=payload.dose,
        time=payload.time,
        frequency=payload.frequency,
        start_date=payload.start_date or today_str,
        end_date=payload.end_date,
        instructions=payload.instructions,
        enabled=True,
        today_status="pending"
    )

@router.get("", response_model=List[ReminderResponse])
def list_reminders(user_id: str):
    """
    Lists all medication reminders for the user, checking today's taken status.
    """
    db = get_db()
    res = db.table("reminders").select("*").eq("user_id", user_id).order("time", desc=False).execute()
    today_str = date.today().isoformat()

    # Fetch today's completed history
    hist_res = db.table("reminder_history").select("*").eq("user_id", user_id).execute()
    hist_rows = hist_res.data if isinstance(hist_res.data, list) else []
    taken_reminder_ids = {
        str(h.get("reminder_id")) 
        for h in hist_rows 
        if isinstance(h, dict) and h.get("status") == "taken" and str(h.get("scheduled_at", "")).startswith(today_str)
    }

    output = []
    reminder_rows = res.data if isinstance(res.data, list) else []
    for item in reminder_rows:
        r: dict = item if isinstance(item, dict) else {}
        rem_id = str(r.get("id", ""))
        st = "taken" if rem_id in taken_reminder_ids else "pending"
        output.append(ReminderResponse(
            id=rem_id,
            user_id=str(r.get("user_id", "")),
            medicine_id=r.get("medicine_id"),
            medicine_name=str(r.get("medicine_name", "Medicine")),
            dose=str(r.get("dose", "1 dose")),
            time=str(r.get("time", "08:00")),
            frequency=str(r.get("frequency", "once_daily")),
            start_date=r.get("start_date"),
            end_date=r.get("end_date"),
            instructions=r.get("instructions"),
            enabled=bool(r.get("enabled", True)),
            created_at=r.get("created_at"),
            today_status=st
        ))
    return output

@router.put("/{id}", response_model=ReminderResponse)
def update_reminder(id: str, enabled: Optional[bool] = None, time: Optional[str] = None):
    db = get_db()
    update_data = {}
    if enabled is not None:
        update_data["enabled"] = enabled
    if time is not None:
        update_data["time"] = time

    db.table("reminders").update(update_data).eq("id", id).execute()
    res = db.table("reminders").select("*").eq("id", id).execute()
    raw_res = res.data if isinstance(res.data, list) else []
    if not raw_res:
        raise HTTPException(status_code=404, detail="Reminder not found")
    r: dict = raw_res[0] if isinstance(raw_res[0], dict) else {}
    return ReminderResponse(
        id=str(r.get("id", id)),
        user_id=str(r.get("user_id", "")),
        medicine_id=r.get("medicine_id"),
        medicine_name=r.get("medicine_name"),
        dose=r.get("dose"),
        time=r.get("time"),
        frequency=r.get("frequency"),
        start_date=r.get("start_date"),
        end_date=r.get("end_date"),
        instructions=r.get("instructions"),
        enabled=bool(r.get("enabled", True)),
        created_at=r.get("created_at"),
        today_status="pending"
    )

@router.delete("/{id}")
def delete_reminder(id: str):
    db = get_db()
    db.table("reminder_history").delete().eq("reminder_id", id).execute()
    db.table("reminders").delete().eq("id", id).execute()
    return {"message": "Reminder deleted successfully", "id": id}

@router.post("/{id}/complete")
def complete_reminder(
    id: str, 
    user_id: Optional[str] = Form(None),
    user_id_query: Optional[str] = Query(None, alias="user_id")
):
    """
    Marks a reminder as TAKEN for today and records adherence in reminder_history.
    """
    db = get_db()
    uid = user_id or user_id_query or "demo-patient-001"
    rem_res = db.table("reminders").select("*").eq("id", id).execute()
    if not rem_res.data:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    rem = rem_res.data[0]
    now_iso = datetime.now().isoformat()
    
    db.table("reminder_history").insert({
        "id": str(uuid.uuid4()),
        "reminder_id": id,
        "user_id": uid,
        "scheduled_at": now_iso,
        "status": "taken",
        "taken_at": now_iso
    }).execute()

    return {"message": f"Recorded: {rem.get('medicine_name')} marked as taken", "status": "taken", "taken_at": now_iso}

@router.get("/history", response_model=List[ReminderHistoryItem])
def get_reminder_history(user_id: str):
    """
    Retrieves adherence history for the patient.
    """
    db = get_db()
    hist_res = db.table("reminder_history").select("*").eq("user_id", user_id).order("scheduled_at", desc=True).limit(50).execute()
    
    # Map reminder IDs to names
    rem_res = db.table("reminders").select("*").eq("user_id", user_id).execute()
    rem_map = {r["id"]: r for r in (rem_res.data or [])}

    output = []
    for h in (hist_res.data or []):
        rem = rem_map.get(h.get("reminder_id"), {})
        output.append(ReminderHistoryItem(
            id=h["id"],
            reminder_id=h["reminder_id"],
            medicine_name=rem.get("medicine_name", "Medication"),
            dose=rem.get("dose", "1 dose"),
            scheduled_at=h.get("scheduled_at"),
            status=h.get("status", "taken"),
            taken_at=h.get("taken_at"),
            created_at=h.get("created_at")
        ))
    return output
