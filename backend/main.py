import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from config import settings, UPLOADS_DIR, SAMPLES_DIR
from api.auth import router as auth_router
from api.prescriptions import router as prescriptions_router
from api.analysis import router as analysis_router
from api.medicines import router as medicines_router
from api.reminders import router as reminders_router
from api.language import router as language_router
from api.pdf import router as pdf_router

app = FastAPI(
    title="MediGuard AI - Medication Safety & Management API",
    description="Backend API powering multi-prescription OCR, drug interaction analysis, dosage safety, and medication planning.",
    version=settings.VERSION
)

# CORS Middleware with valid origin reflection for credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploaded prescription images & PDF samples
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/samples", StaticFiles(directory=str(SAMPLES_DIR)), name="samples")

# Register routers with both /api prefix and root prefix for maximum client flexibility
routers = [
    auth_router,
    analysis_router,
    prescriptions_router,
    medicines_router,
    reminders_router,
    language_router,
    pdf_router
]

for r in routers:
    app.include_router(r, prefix="/api")
    app.include_router(r)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "MediGuard AI",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to MediGuard AI API - AI-Powered Prescription Safety & Medication Management System",
        "docs_url": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
