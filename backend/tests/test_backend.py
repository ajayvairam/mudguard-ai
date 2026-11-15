import pytest
from services.medicine_normalization import normalize_medicine_name, extract_strength_mg, parse_frequency_per_day
from services.interaction_service import check_pairwise_interaction, analyze_all_drug_interactions
from services.duplicate_detection import detect_duplicates_and_overlaps
from services.dosage_analysis import analyze_dosage_and_conflicts
from services.pdf_service import generate_medication_summary_pdf

def test_normalization_dolo():
    norm = normalize_medicine_name("Dolo 650")
    assert norm["generic_name"] == "Paracetamol"
    assert norm["active_ingredient"] == "Paracetamol"
    assert norm["max_daily_dose_mg"] == 4000

def test_normalization_combiflam():
    norm = normalize_medicine_name("Combiflam")
    assert norm["active_ingredient"] in ["Ibuprofen", "Diclofenac", "Paracetamol"]

def test_extract_strength_mg():
    assert extract_strength_mg("650 mg") == 650.0
    assert extract_strength_mg("1 g") == 1000.0
    assert extract_strength_mg("0.5 mg") == 0.5
    assert extract_strength_mg("400mg") == 400.0

def test_parse_frequency_per_day():
    assert parse_frequency_per_day("once daily") == 1.0
    assert parse_frequency_per_day("twice daily") == 2.0
    assert parse_frequency_per_day("1-0-1") == 2.0
    assert parse_frequency_per_day("1-1-1") == 3.0
    assert parse_frequency_per_day("three times daily") == 3.0

def test_drug_interaction_aspirin_warfarin():
    interaction = check_pairwise_interaction("Aspirin", "Warfarin")
    assert interaction is not None
    assert interaction["severity"] == "CRITICAL"

def test_drug_interaction_clopidogrel_omeprazole():
    interaction = check_pairwise_interaction("Clopidogrel", "Omeprazole")
    assert interaction is not None
    assert interaction["severity"] == "HIGH"

def test_duplicate_and_overlap_detection():
    meds = [
        {
            "id": "1",
            "prescription_id": "rx1",
            "original_name": "Dolo 650",
            "active_ingredient": "Paracetamol",
            "strength": "650 mg",
            "frequency": "three times daily"
        },
        {
            "id": "2",
            "prescription_id": "rx2",
            "original_name": "Crocin 500",
            "active_ingredient": "Paracetamol",
            "strength": "500 mg",
            "frequency": "twice daily"
        }
    ]
    rx_map = {
        "rx1": {"doctor_name": "Dr. Kumar"},
        "rx2": {"doctor_name": "Dr. Ravi"}
    }
    warnings = detect_duplicates_and_overlaps(meds, rx_map)
    assert any(w.analysis_type == "duplicate" for w in warnings)

def test_dosage_concern_excessive_paracetamol():
    # 650mg * 3 = 1950mg + 1000mg * 3 = 3000mg -> 4950mg/day (> 4000mg limit)
    meds = [
        {
            "id": "1",
            "prescription_id": "rx1",
            "original_name": "Dolo 650",
            "active_ingredient": "Paracetamol",
            "max_daily_dose_mg": 4000,
            "strength": "650 mg",
            "frequency": "three times daily"
        },
        {
            "id": "2",
            "prescription_id": "rx2",
            "original_name": "Paracetamol 1000",
            "active_ingredient": "Paracetamol",
            "max_daily_dose_mg": 4000,
            "strength": "1000 mg",
            "frequency": "three times daily"
        }
    ]
    rx_map = {"rx1": {"doctor_name": "Dr. A"}, "rx2": {"doctor_name": "Dr. B"}}
    warnings = analyze_dosage_and_conflicts(meds, rx_map)
    dosage_warns = [w for w in warnings if w.analysis_type == "dosage_concern"]
    assert len(dosage_warns) > 0
    assert dosage_warns[0].daily_exposure_mg > 4000

def test_pdf_generation():
    dummy_data = {
        "prescriptions": [{"file_name": "rx.png", "doctor_name": "Dr. Smith", "prescription_date": "2026-09-04", "medicines_count": 2}],
        "consolidated_plan": [{
            "medicine_name": "Amoxicillin 500 mg",
            "strength": "500 mg",
            "dosage": "1 cap",
            "frequency": "twice daily",
            "duration": "7 days",
            "requires_review": False,
            "schedule_slots": ["Morning", "Night"]
        }],
        "warnings": [{
            "analysis_type": "duplicate",
            "severity": "HIGH",
            "medicine_a_name": "Paracetamol",
            "medicine_b_name": "Dolo",
            "concern": "Double dosing",
            "recommendation": "Consult doctor"
        }]
    }
    pdf_bytes = generate_medication_summary_pdf(dummy_data, patient_name="Test Patient")
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")
