import uuid
from fastapi import APIRouter, HTTPException, Depends
from models.schemas import UserProfile
from database.supabase_client import get_db

router = APIRouter(prefix="", tags=["Authentication & Profile"])

@router.post("/auth/profile", response_model=UserProfile)
def create_or_update_profile(profile: UserProfile):
    """
    Creates or updates a user profile record in the database, preserving language preference.
    """
    db = get_db()
    existing = db.table("profiles").select("*").eq("user_id", profile.user_id).execute()
    
    data = {
        "user_id": profile.user_id,
        "full_name": profile.full_name or "Patient",
        "email": profile.email or "patient@mediguard.ai",
        "avatar_url": profile.avatar_url,
        "preferred_language": profile.preferred_language or "en"
    }

    if existing.data and len(existing.data) > 0:
        db.table("profiles").update(data).eq("user_id", profile.user_id).execute()
    else:
        # Provide required primary key id for PostgreSQL table
        data["id"] = str(uuid.uuid4())
        db.table("profiles").insert(data).execute()

    return profile

@router.get("/auth/profile/{user_id}", response_model=UserProfile)
def get_user_profile(user_id: str):
    """
    Retrieves user profile and current language settings.
    """
    db = get_db()
    res = db.table("profiles").select("*").eq("user_id", user_id).execute()
    raw_data = res.data if isinstance(res.data, list) else []
    if raw_data:
        first = raw_data[0]
        row: dict = first if isinstance(first, dict) else {}
        return UserProfile(
            user_id=str(row.get("user_id", user_id)),
            full_name=row.get("full_name") or "Patient",
            email=row.get("email") or "patient@mediguard.ai",
            avatar_url=row.get("avatar_url"),
            preferred_language=row.get("preferred_language") or "en"
        )
    return UserProfile(user_id=user_id, full_name="Patient", email="patient@mediguard.ai", preferred_language="en")
