import json
import re
from typing import Dict, Any, Optional, List
from config import settings
from models.schemas import PrescriptionExtractionSchema, ExtractedMedicine

HAS_GEMINI = bool(settings.GEMINI_API_KEY and "your-gemini" not in settings.GEMINI_API_KEY)

gemini_model = None
if HAS_GEMINI:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Use gemini-3.6-flash as recommended by the Gemini API
        gemini_model = genai.GenerativeModel("models/gemini-3.6-flash")
        print("Google Gemini model initialized successfully.")
    except Exception as e:
        print(f"Warning: Failed to configure Google Gemini: {e}")
        gemini_model = None

EXTRACTION_SYSTEM_PROMPT = """
You are a prescription information extraction assistant.
Extract only information explicitly present in the supplied prescription text.
Do not invent missing information.
Return valid JSON adhering to this exact schema:
{
  "doctor_name": "Dr. Full Name",
  "prescription_date": "YYYY-MM-DD",
  "patient_name": "Patient Name if present",
  "medicines": [
    {
      "original_name": "Exact Brand / Medicine Name",
      "generic_name": "Generic Name if known or obvious",
      "strength": "e.g. 500 mg, 10 mg",
      "dosage": "e.g. 1 tablet, 5 ml",
      "frequency": "e.g. twice daily, 1-0-1, once daily",
      "duration": "e.g. 5 days, 30 days",
      "route": "oral",
      "instructions": "e.g. after food, empty stomach",
      "confidence": 0.95
    }
  ],
  "notes": "Any other explicit clinical notes"
}

Safety Rules:
- Do not diagnose diseases.
- Do not prescribe medicines.
- Do not modify dosage.
- If information is uncertain, lower the confidence score.
"""

EXPLANATION_SYSTEM_PROMPT = """
You are a patient-friendly medication safety communicator.
Explain the verified medication safety result in simple, compassionate, and clear patient-friendly language.
Do not add medical facts that are not present in the verified source information.
Do not tell the patient to stop medication autonomously.
Clearly recommend consultation with a qualified doctor or pharmacist when appropriate.
"""

def extract_medicines_with_gemini(raw_text: str) -> Optional[PrescriptionExtractionSchema]:
    """
    Extracts structured medicine entities from raw prescription text using Gemini,
    with strict JSON parsing and Pydantic validation.
    """
    if not gemini_model or not raw_text.strip():
        return None

    prompt = f"{EXTRACTION_SYSTEM_PROMPT}\n\nPrescription text to extract:\n\"\"\"\n{raw_text}\n\"\"\""
    try:
        response = gemini_model.generate_content(prompt)
        text_resp = response.text.strip()
        # Clean markdown code blocks if wrapped
        if text_resp.startswith("```json"):
            text_resp = text_resp[7:]
        if text_resp.startswith("```"):
            text_resp = text_resp[3:]
        if text_resp.endswith("```"):
            text_resp = text_resp[:-3]
        text_resp = text_resp.strip()

        data = json.loads(text_resp)
        return PrescriptionExtractionSchema.model_validate(data)
    except Exception as e:
        print(f"Gemini extraction encountered error or invalid JSON: {e}")
        return None

import time
_gemini_cooldown_until = 0.0

def generate_friendly_explanation(
    warning_type: str, 
    medicine_a: str, 
    medicine_b: Optional[str], 
    clinical_desc: str, 
    target_language: str = "en"
) -> str:
    """
    Generates a clear patient explanation using Gemini or structured deterministic templates.
    """
    global _gemini_cooldown_until
    lang_name = settings.SUPPORTED_LANGUAGES.get(target_language, "English")
    now = time.time()
    
    if gemini_model and now > _gemini_cooldown_until:
        try:
            prompt = (
                f"{EXPLANATION_SYSTEM_PROMPT}\n"
                f"Warning Type: {warning_type}\n"
                f"Medicine A: {medicine_a}\n"
                f"Medicine B: {medicine_b or 'None'}\n"
                f"Clinical Details: {clinical_desc}\n"
                f"Target Language: {lang_name}\n\n"
                f"Provide a 2-3 sentence patient-friendly explanation in {lang_name}."
            )
            response = gemini_model.generate_content(prompt, request_options={"timeout": 6.0})
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "quota" in err_str.lower() or "504" in err_str:
                _gemini_cooldown_until = now + 60.0
                print("Notice: Gemini rate limit/quota reached. Using instantaneous clinical fallback engine.")
            else:
                print(f"Gemini explanation notice: {e}")

    # High-quality deterministic fallback
    if warning_type == "duplicate":
        return f"Notice: {medicine_a} or its active ingredient appears more than once across your prescriptions. Taking multiple products with the same ingredient can cause accidental double dosing. Please check with your doctor."
    elif warning_type == "interaction":
        return f"Safety Notice: {medicine_a} and {medicine_b} may influence each other's effects when taken together. Please discuss this combination with your doctor or pharmacist to confirm if timing or monitoring is advised."
    elif warning_type == "dosage_concern":
        return f"Dosage Notice: The total combined daily amount of {medicine_a} across your prescriptions appears high. Please verify the intended schedule with your healthcare provider."
    elif warning_type == "overlap":
        return f"Therapeutic Overlap: {medicine_a} and {medicine_b} serve similar medical purposes. Confirm with your doctor whether both should be taken concurrently."
    
    return clinical_desc
