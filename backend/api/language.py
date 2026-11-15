import uuid
from fastapi import APIRouter, HTTPException, Form, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
from database.supabase_client import get_db
from services.translation_service import translate_explanation
from services.speech_service import prepare_speech_payload, generate_speech_audio
from config import settings

router = APIRouter(prefix="", tags=["Language & Voice Assistance"])

class TranslationRequest(BaseModel):
    text: str
    target_language: str # en, ta, te, hi, ml, kn, bn, mr

@router.put("/language")
def update_language_preference(user_id: str = Form(...), preferred_language: str = Form(...)):
    """
    Updates the user's preferred language directly in the database from the navbar
    without requiring any Profile page.
    """
    if preferred_language not in settings.SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language code: {preferred_language}")

    db = get_db()
    existing = db.table("profiles").select("*").eq("user_id", user_id).execute()
    if existing.data:
        db.table("profiles").update({"preferred_language": preferred_language}).eq("user_id", user_id).execute()
    else:
        db.table("profiles").insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "preferred_language": preferred_language
        }).execute()

    return {
        "user_id": user_id,
        "preferred_language": preferred_language,
        "language_name": settings.SUPPORTED_LANGUAGES.get(preferred_language)
    }

@router.post("/language/translate")
def translate_text_endpoint(payload: TranslationRequest):
    """
    Translates verified medical safety alert or instructions into regional language.
    """
    translated = translate_explanation(payload.text, payload.target_language)
    return {
        "original_text": payload.text,
        "target_language": payload.target_language,
        "translated_text": translated
    }

@router.post("/language/speech")
def speech_payload_endpoint(payload: TranslationRequest):
    """
    Generates voice-ready speech synthesis payload with embedded authentic regional MP3 audio.
    """
    translated = translate_explanation(payload.text, payload.target_language) if payload.target_language != "en" else payload.text
    speech_data = prepare_speech_payload(translated, payload.target_language)
    speech_data["original_text"] = payload.text
    return speech_data

@router.get("/language/audio")
def get_audio_stream(text: str = Query(...), lang: str = Query("en")):
    """
    Direct binary audio streaming endpoint for browser HTML5 <audio> elements.
    """
    audio_bytes, mime = generate_speech_audio(text, lang)
    return StreamingResponse(io.BytesIO(audio_bytes), media_type=mime)
