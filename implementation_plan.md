# MediGuard AI — Implementation Plan

## Goal Description
Build **MediGuard AI**, a complete, production-quality full-stack healthcare application designed to protect patients who receive prescriptions from multiple doctors. The system identifies duplicate medicines, identical active ingredients under different brand names, medication overlap, potential drug-drug interactions, dosage conflicts, excessive total daily exposure, and conflicting instructions. It provides patient-friendly regional-language explanations (English + 7 Indian languages: Tamil, Telugu, Hindi, Malayalam, Kannada, Bengali, Marathi), voice assistance, a consolidated medication review summary, downloadable PDF generation, and medication reminders with adherence tracking.

The application strictly enforces a **medication safety assistant** boundary (not an autonomous prescriber), and explicitly abides by the rule: **No Profile page or Profile navigation item anywhere**, with language selection directly available in the navbar.

---

## User Review Required

> [!IMPORTANT]
> **Authentication & Offline/Local Fallback Strategy**:
> MediGuard AI is architected to use **Supabase Auth (Google OAuth)**, **Supabase PostgreSQL**, and **Supabase Storage**. However, to ensure seamless immediate testing and zero-friction evaluation on your local machine without requiring you to immediately configure Google Cloud Console OAuth credentials or Supabase project keys, the backend includes an intelligent dual-mode:
> 1. If `SUPABASE_URL` and keys are provided in `.env`, it uses Supabase Auth, PostgreSQL, and Storage.
> 2. If keys are omitted or empty, it automatically falls back to a robust SQLite + local storage and one-click "Demo / Instant Test Login" mode alongside the Google OAuth button, ensuring 100% functionality out of the box.

> [!IMPORTANT]
> **AI Architecture & Drug Safety Dual Verification**:
> Per Section 18 & 52 of your specification, **drug interactions are NEVER hallucinated by LLMs**. We will implement a verified clinical drug interaction database (bundled with 200+ major prescription drug classes, FDA guidelines, and active ingredients) combined with optional OpenFDA lookups. Google Gemini (`google-genai` / `google-generativeai`) is used strictly for OCR interpretation, structured extraction with Pydantic validation, patient-friendly explanations, and regional language translations.

---

## Proposed Architecture & File Structure

```text
mediguardai/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py                  # User authentication, profile sync, language preference
│   │   ├── prescriptions.py         # Multi-file prescription upload, OCR, listing, deletion
│   │   ├── analysis.py              # Prescription analysis pipeline, safety check, confirm
│   │   ├── medicines.py             # Medicine CRUD, normalization, user correction
│   │   ├── reminders.py             # Reminders CRUD, today's schedule, mark taken, history
│   │   ├── language.py              # Language update, Gemini translations, TTS speech audio
│   │   └── pdf.py                   # PDF generation endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_service.py           # OCR text extraction (PDFs, scans, images + Gemini fallback)
│   │   ├── gemini_service.py        # Gemini client for structured extraction & explanations
│   │   ├── medicine_extraction.py   # Medicine parsing & confidence evaluation
│   │   ├── medicine_normalization.py# Normalize to generic name, active ingredients, strength
│   │   ├── interaction_service.py   # Trusted clinical interaction engine (severity, evidence)
│   │   ├── duplicate_detection.py   # Exact duplicate & duplicate active ingredient detection
│   │   ├── dosage_analysis.py       # Daily exposure calculations & maximum threshold checks
│   │   ├── consolidation_service.py # Proposed Consolidated Medication Review builder
│   │   ├── translation_service.py   # Regional language translation with Gemini
│   │   ├── speech_service.py        # Text-to-speech audio service
│   │   └── pdf_service.py           # ReportLab professional PDF generation matching Section 27
│   ├── database/
│   │   ├── __init__.py
│   │   ├── supabase_client.py       # Supabase client + local fallback store
│   │   └── schema.sql               # Complete PostgreSQL Supabase schema with RLS & storage
│   ├── data/
│   │   ├── drug_database.json       # Trusted reference database (active ingredients, limits)
│   │   └── drug_interactions.json   # Verified clinical interactions & severity rules
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py               # Pydantic schemas for request/response validation
│   ├── samples/                     # Realistic multi-doctor sample prescriptions for testing
│   │   ├── dr_kumar_prescription.png
│   │   ├── dr_ravi_prescription.png
│   │   └── dr_priya_prescription.pdf
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx           # Clean navbar: exact links + Language dropdown + Logout
│   │   │   ├── PrescriptionUploader.jsx # Drag-drop multi-file uploader + sample presets
│   │   │   ├── PrescriptionCard.jsx # Preview card with doctor, date, status, remove
│   │   │   ├── AnalysisProgress.jsx # Animated step-by-step clinical analysis progress
│   │   │   ├── MedicineCard.jsx     # Medicine view & interactive edit modal
│   │   │   ├── InteractionWarning.jsx # Severity badge (LOW/MODERATE/HIGH/CRITICAL) + Listen
│   │   │   ├── DuplicateWarning.jsx # Duplicate active ingredient warning + details
│   │   │   ├── DosageWarning.jsx    # Combined exposure breakdown vs daily safe limit
│   │   │   ├── OverlapWarning.jsx   # Therapeutic class overlap details
│   │   │   ├── VoiceButton.jsx      # Regional language voice synthesis player
│   │   │   ├── LanguageSelector.jsx # Navbar dropdown for 8 languages
│   │   │   ├── ReminderCard.jsx     # Medication reminder card with time badges
│   │   │   └── SafetyBanner.jsx     # Prominent healthcare disclaimer banner
│   │   ├── pages/
│   │   │   ├── Landing.jsx          # Healthcare landing page with features & CTA
│   │   │   ├── Login.jsx            # Google sign-in + instant test login
│   │   │   ├── Dashboard.jsx        # Stats, +Upload CTA, Today's schedule with "Mark Taken"
│   │   │   ├── UploadPrescription.jsx# Multi-prescription upload page with sample loader
│   │   │   ├── Analysis.jsx         # Full analysis results, warnings, editable medicine table
│   │   │   ├── MedicationPlan.jsx   # Consolidated Medication Review Summary + PDF download
│   │   │   ├── Reminders.jsx        # Reminders management, custom times, history log
│   │   │   └── History.jsx          # Past prescription analyses, re-analyse, PDF export
│   │   ├── services/
│   │   │   ├── api.js               # Axios instance with baseURL and auth headers
│   │   │   ├── supabase.js          # Supabase JS client
│   │   │   └── auth.js              # Auth helper functions
│   │   ├── context/
│   │   │   ├── AuthContext.jsx      # User state, sign-in, sign-out
│   │   │   └── LanguageContext.jsx  # Active language state, translation loader
│   │   ├── i18n/
│   │   │   ├── en.json              # English
│   │   │   ├── ta.json              # Tamil (தமிழ்)
│   │   │   ├── te.json              # Telugu (తెలుగు)
│   │   │   ├── hi.json              # Hindi (हिन्दी)
│   │   │   ├── ml.json              # Malayalam (മലയാളം)
│   │   │   ├── kn.json              # Kannada (ಕನ್ನಡ)
│   │   │   ├── bn.json              # Bengali (বাংলা)
│   │   │   └── mr.json              # Marathi (मराठी)
│   │   ├── App.jsx                  # React Router routes & protective layout
│   │   ├── index.css                # Tailwind CSS directives & custom healthcare styling
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── .env.example
└── README.md
```

---

## Proposed Changes by Component

### 1. Database & Security (`backend/database/schema.sql`)
- PostgreSQL DDL for tables: `profiles`, `prescriptions`, `medicines`, `medication_analysis`, `consolidated_medications`, `reminders`, `reminder_history`.
- Foreign key constraints, cascade rules, and updated_at triggers.
- Row Level Security (RLS) policies enforcing `auth.uid() = user_id`.
- Supabase Storage bucket definition for `prescriptions`.

### 2. Clinical Data & Interaction Engine (`backend/data/` & `backend/services/`)
- `drug_database.json`: Comprehensive database of medicines (Paracetamol/Acetaminophen, Amoxicillin, Ibuprofen, Atorvastatin, Metformin, Clopidogrel, Aspirin, Omeprazole, Lisinopril, Amlodipine, Tramadol, Ciprofloxacin, Warfarin, etc.), active ingredients, therapeutic classes, standard dosage limits.
- `drug_interactions.json`: High-precision interaction matrix cataloguing interactions with severity (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`), mechanism of action, clinical evidence, and recommended action.
- `interaction_service.py`: Computes pairwise drug-drug interactions for any set of identified medicines. If interaction information cannot be reliably determined, returns the required message: *"Interaction information could not be reliably determined. Please consult a pharmacist or doctor."*
- `duplicate_detection.py`: Identifies both brand name duplicates and identical active ingredients across multiple prescriptions.
- `dosage_analysis.py`: Calculates daily exposure (strength × frequency) across all prescriptions and flags potential exceeding of daily therapeutic limits.

### 3. Gemini AI Service & OCR (`backend/services/`)
- `ocr_service.py`: Handles image decoding, PDF page rasterization/text extraction, and passes to OCR engine / Gemini Vision for high accuracy medical handwriting and printed text recognition.
- `gemini_service.py`: Structured extraction with strict Pydantic models. Generates patient-friendly explanations in simple terms without inventing unverified claims.
- `translation_service.py`: Translates explanations and warnings into Tamil, Telugu, Hindi, Malayalam, Kannada, Bengali, and Marathi while preserving critical medical names and dosages.
- `pdf_service.py`: ReportLab generator producing the official "MediGuard AI — Consolidated Medication Summary" PDF including Patient details, Analysis date, Sources, Medication schedule (Morning/Afternoon/Evening/Night), Duplicate warnings, Interaction alerts, Dosage concerns, and the mandatory healthcare disclaimer.

### 4. FastAPI Endpoints (`backend/api/` & `backend/main.py`)
- Full REST API with CORS, error handlers, and file upload endpoints.
- Preloaded sample data endpoints so users can immediately test multi-doctor prescriptions with 1 click.

### 5. Frontend UI & Experience (`frontend/src/`)
- **Landing Page**: Modern healthcare aesthetics, hero headline *"Your Prescriptions. One Safer Medication Plan."*, feature cards, safety disclaimer, Google OAuth CTA.
- **Navbar**: Strictly contains: `Dashboard`, `Prescriptions`, `Analysis`, `Medications`, `Reminders`, `History`, `Language Selector dropdown`, `Logout`. **Zero mention of Profile.**
- **Prescription Upload**: Multi-file dropzone with image/PDF previews, doctor & date tagging, and a "Load Realistic Multi-Doctor Sample Prescriptions" quick-test button.
- **Analysis View**: Visual progress bar, summary metrics, severity-coded cards with text labels (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`), Voice button (`[🔊 Listen]`), editable medicine verification table, and confirmation workflow.
- **Consolidated Summary**: Morning/Afternoon/Evening/Night schedule, "REVIEW REQUIRED" badges, PDF download trigger, and Reminders integration.
- **Reminders**: Today's schedule with "Mark as Taken", custom reminder scheduler, adherence percentage, and history logs.
- **8 Indian Languages**: Full translation keys for all navigation, buttons, warnings, and messages.

---

## Verification Plan

### Automated & Backend Verification
1. Run backend tests with `pytest` checking:
   - Medicine normalization and active ingredient mapping.
   - Duplicate medicine detection logic.
   - Drug-drug interaction engine output against known pairs (e.g. Aspirin + Warfarin, Ibuprofen + Lisinopril).
   - Dosage limit calculations (e.g. Paracetamol > 4000 mg/day).
   - Pydantic schema validation for Gemini structured output.
   - PDF generation creating valid PDF byte stream.
2. Verify FastAPI startup on `http://localhost:8000` with Swagger docs at `/docs`.

### Frontend & End-to-End Verification
1. Run `npm run build` to verify clean compilation with no TypeScript/JSX errors.
2. Launch Vite dev server on `http://localhost:5173`.
3. Test using the interactive browser agent:
   - Verify Landing page layout, navigation, and disclaimer.
   - Test login / authentication.
   - Test uploading multiple prescriptions (e.g. Dr. Kumar, Dr. Ravi, Dr. Priya).
   - Verify multi-step analysis progress display.
   - Inspect detected duplicate medicines, active ingredient overlap, dosage concerns, and drug interactions.
   - Test language switching to Tamil (தமிழ்) and Hindi (हिन्दी) to confirm live UI translation.
   - Test the voice button `[🔊 Listen]` for audible warning explanation.
   - Edit an OCR extraction in the verification table.
   - Confirm and generate the Consolidated Medication Summary.
   - Trigger and verify PDF generation.
   - Add a medication reminder and mark it as taken on the Dashboard.
   - Verify History page records the analysis.
