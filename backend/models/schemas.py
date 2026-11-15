from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Profile schemas
class UserProfile(BaseModel):
    user_id: str
    full_name: Optional[str] = "Demo Patient"
    email: Optional[str] = "patient@mediguard.ai"
    avatar_url: Optional[str] = None
    preferred_language: str = "en"

class LanguageUpdateRequest(BaseModel):
    preferred_language: str

# Medicine extraction schemas (Gemini Structured Output)
class ExtractedMedicine(BaseModel):
    original_name: str = Field(description="Medicine name as written on prescription")
    generic_name: Optional[str] = Field(None, description="Standard pharmaceutical or generic name")
    strength: Optional[str] = Field(None, description="Dosage strength e.g., '500 mg', '10 mg'")
    dosage: Optional[str] = Field(None, description="Dose form or quantity e.g., '1 tablet', '5 ml'")
    frequency: Optional[str] = Field(None, description="Administration frequency e.g., 'twice daily', '1-0-1'")
    duration: Optional[str] = Field(None, description="Treatment duration e.g., '5 days', '30 days'")
    route: Optional[str] = Field("oral", description="Route e.g., 'oral', 'topical'")
    instructions: Optional[str] = Field(None, description="Special instructions e.g., 'after food', 'before bedtime'")
    confidence: float = Field(0.95, description="Extraction confidence score from 0.0 to 1.0")

class PrescriptionExtractionSchema(BaseModel):
    doctor_name: Optional[str] = Field(None, description="Prescribing physician name")
    prescription_date: Optional[str] = Field(None, description="Date of prescription")
    patient_name: Optional[str] = Field(None, description="Patient name if visible")
    medicines: List[ExtractedMedicine] = Field(default_factory=list)
    notes: Optional[str] = Field(None, description="Additional notes or diagnosis on prescription")

# Database Medicine Representation
class MedicineBase(BaseModel):
    original_name: str
    normalized_name: Optional[str] = None
    generic_name: Optional[str] = None
    active_ingredient: Optional[str] = None
    strength: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    route: Optional[str] = "oral"
    instructions: Optional[str] = None
    confidence: float = 0.95
    requires_verification: bool = False

class MedicineResponse(MedicineBase):
    id: str
    prescription_id: str
    user_id: str
    created_at: Optional[str] = None
    doctor_name: Optional[str] = None

class MedicineUpdateRequest(BaseModel):
    original_name: Optional[str] = None
    generic_name: Optional[str] = None
    strength: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    instructions: Optional[str] = None
    requires_verification: Optional[bool] = False

# Prescription schemas
class PrescriptionResponse(BaseModel):
    id: str
    user_id: str
    file_url: Optional[str] = None
    file_name: str
    file_type: Optional[str] = None
    doctor_name: Optional[str] = None
    prescription_date: Optional[str] = None
    raw_text: Optional[str] = None
    ocr_confidence: float = 1.0
    status: str = "uploaded"
    created_at: Optional[str] = None
    medicines_count: Optional[int] = 0

# Safety & Analysis schemas
class WarningItem(BaseModel):
    id: Optional[str] = None
    medicine_a_id: Optional[str] = None
    medicine_b_id: Optional[str] = None
    medicine_a_name: str
    medicine_b_name: Optional[str] = None
    analysis_type: str # duplicate, interaction, overlap, dosage_concern, conflict
    severity: str # LOW, MODERATE, HIGH, CRITICAL
    description: str
    concern: Optional[str] = None
    recommendation: str
    source: Optional[str] = "MediGuard Clinical Pharmacology Knowledgebase"
    daily_exposure_mg: Optional[float] = None
    safe_daily_limit_mg: Optional[float] = None
    prescription_sources: Optional[List[str]] = None

class AnalysisStatistics(BaseModel):
    total_prescriptions: int
    total_medicines: int
    duplicate_count: int
    interaction_count: int
    dosage_concern_count: int
    overlap_count: int
    conflict_count: int
    clean_medicines_count: int

class ConsolidatedMedication(BaseModel):
    id: Optional[str] = None
    medicine_name: str
    generic_name: Optional[str] = None
    strength: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    instructions: Optional[str] = None
    status: str = "active"
    requires_review: bool = False
    review_reason: Optional[str] = None
    source_prescriptions: List[str] = []
    schedule_slots: List[str] = [] # Morning, Afternoon, Evening, Night

class FullAnalysisResponse(BaseModel):
    analysis_id: str
    statistics: AnalysisStatistics
    prescriptions: List[PrescriptionResponse]
    medicines: List[MedicineResponse]
    warnings: List[WarningItem]
    consolidated_plan: List[ConsolidatedMedication]
    created_at: str

# Reminder schemas
class ReminderCreateRequest(BaseModel):
    medicine_id: Optional[str] = None
    medicine_name: str
    dose: str
    time: str # HH:MM
    frequency: str = "once_daily" # once_daily, twice_daily, three_daily, custom
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    instructions: Optional[str] = None

class ReminderResponse(BaseModel):
    id: str
    user_id: str
    medicine_id: Optional[str] = None
    medicine_name: str
    dose: str
    time: str
    frequency: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    instructions: Optional[str] = None
    enabled: bool = True
    created_at: Optional[str] = None
    today_status: Optional[str] = "pending" # pending, taken, missed

class ReminderHistoryItem(BaseModel):
    id: str
    reminder_id: str
    medicine_name: Optional[str] = None
    dose: Optional[str] = None
    scheduled_at: str
    status: str # pending, taken, missed
    taken_at: Optional[str] = None
    created_at: Optional[str] = None
