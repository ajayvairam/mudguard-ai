import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent

# Load .env file so os.getenv picks up the keys
load_dotenv(BASE_DIR / ".env")
DATA_DIR = BASE_DIR / "data"
SAMPLES_DIR = BASE_DIR / "samples"
UPLOADS_DIR = BASE_DIR / "uploads"

# Ensure runtime directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    PROJECT_NAME: str = "MediGuard AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Supabase Settings
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Gemini AI Key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Optional Drug DB API Key
    DRUG_DATABASE_API_KEY: str = os.getenv("DRUG_DATABASE_API_KEY", "")
    
    # Server & CORS
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Supported regional languages
    SUPPORTED_LANGUAGES: dict[str, str] = {
        "en": "English",
        "ta": "Tamil (தமிழ்)",
        "te": "Telugu (తెలుగు)",
        "hi": "Hindi (हिन्दी)",
        "ml": "Malayalam (മലയാളം)",
        "kn": "Kannada (ಕನ್ನಡ)",
        "bn": "Bengali (বাংলা)",
        "mr": "Marathi (मराठी)"
    }

settings = Settings()
