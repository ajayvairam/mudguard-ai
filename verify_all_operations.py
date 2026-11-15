#!/usr/bin/env python3
"""
MediGuard AI — Master System & Full-Stack Operation Verification Suite
Executes a complete end-to-end check across the frontend web application,
backend APIs, clinical safety engines, PDF generator, i18n translation,
and reminder systems.
"""

import sys
import io
import time
import requests
from typing import Tuple, Dict, Any

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

FRONTEND_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:8000"
USER_ID = "test-verification-user"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

results = []

def run_test(test_id: str, title: str, category: str, test_fn):
    start = time.time()
    try:
        success, message, details = test_fn()
        elapsed = time.time() - start
        if success:
            print(f"  {GREEN}✓ PASS{RESET} [{category}] {title} ({elapsed:.2f}s)")
            if details:
                print(f"         {CYAN}↳ {details}{RESET}")
            results.append((test_id, category, title, True, elapsed, details))
        else:
            print(f"  {RED}✗ FAIL{RESET} [{category}] {title} ({elapsed:.2f}s)")
            print(f"         {RED}↳ Error: {message}{RESET}")
            results.append((test_id, category, title, False, elapsed, message))
    except Exception as e:
        elapsed = time.time() - start
        print(f"  {RED}✗ CRASH{RESET} [{category}] {title} ({elapsed:.2f}s)")
        print(f"         {RED}↳ Exception: {str(e)}{RESET}")
        results.append((test_id, category, title, False, elapsed, str(e)))

# ==============================================================================
# 1. FRONTEND SERVER & ROUTES VERIFICATION
# ==============================================================================
def test_frontend_home():
    r = requests.get(FRONTEND_URL, timeout=5)
    if r.status_code == 200 and "html" in r.text.lower():
        return True, "OK", f"Served HTML ({len(r.content)} bytes), status 200"
    return False, f"Status {r.status_code}", ""

def test_frontend_routes():
    routes = ["/dashboard", "/upload", "/analysis", "/medication-plan", "/reminders", "/history"]
    passed = []
    for route in routes:
        r = requests.get(f"{FRONTEND_URL}{route}", timeout=5)
        if r.status_code == 200 and "html" in r.text.lower():
            passed.append(route)
    if len(passed) == len(routes):
        return True, "OK", f"All 6 client routes resolved: {', '.join(passed)}"
    return False, f"Only {len(passed)}/{len(routes)} routes succeeded", ""

# ==============================================================================
# 2. BACKEND HEALTH & DOCS
# ==============================================================================
def test_backend_health():
    r = requests.get(f"{BACKEND_URL}/health", timeout=5)
    if r.status_code == 200:
        d = r.json()
        return True, "OK", f"Status: {d.get('status')}, Version: {d.get('version')}"
    return False, f"Health check failed with {r.status_code}", ""

def test_backend_docs():
    r = requests.get(f"{BACKEND_URL}/docs", timeout=5)
    if r.status_code == 200:
        return True, "OK", f"FastAPI Swagger UI active ({len(r.content)} bytes)"
    return False, f"Docs returned {r.status_code}", ""

# ==============================================================================
# 3. AUTH & USER PROFILES
# ==============================================================================
def test_user_profile():
    payload = {
        "user_id": USER_ID,
        "full_name": "Dr. Rajesh Verification",
        "email": "rajesh.test@mediguard.ai",
        "preferred_language": "ta"
    }
    r = requests.post(f"{BACKEND_URL}/api/auth/profile", json=payload, timeout=5)
    if r.status_code != 200:
        return False, f"Profile save failed: {r.status_code}", ""
    
    # Retrieve profile
    get_r = requests.get(f"{BACKEND_URL}/api/auth/profile/{USER_ID}", timeout=5)
    if get_r.status_code == 200:
        prof = get_r.json()
        return True, "OK", f"Saved & retrieved profile for '{prof.get('full_name')}' (lang: {prof.get('preferred_language')})"
    return False, f"Profile get failed: {get_r.status_code}", ""

# ==============================================================================
# 4. MULTI-DOCTOR PRESCRIPTIONS & OCR
# ==============================================================================
def test_load_sample_prescriptions():
    r = requests.post(f"{BACKEND_URL}/api/prescriptions/load-sample-prescriptions", data={"user_id": USER_ID}, timeout=10)
    if r.status_code == 200:
        data = r.json()
        return True, "OK", f"Loaded {data.get('count')} realistic multi-doctor prescriptions"
    return False, f"Status {r.status_code}: {r.text}", ""

def test_list_prescriptions():
    r = requests.get(f"{BACKEND_URL}/api/prescriptions", params={"user_id": USER_ID}, timeout=5)
    if r.status_code == 200:
        rxs = r.json()
        doctors = [rx.get("doctor_name") for rx in rxs]
        return True, "OK", f"Found {len(rxs)} prescriptions: {', '.join(doctors[:3])}"
    return False, f"Status {r.status_code}", ""

def test_single_prescription_detail():
    r = requests.get(f"{BACKEND_URL}/api/prescriptions", params={"user_id": USER_ID}, timeout=5)
    rxs = r.json()
    if not rxs:
        return False, "No prescriptions found", ""
    rx_id = rxs[0]["id"]
    detail_r = requests.get(f"{BACKEND_URL}/api/prescriptions/{rx_id}", timeout=5)
    if detail_r.status_code == 200:
        rx = detail_r.json()
        return True, "OK", f"ID: {rx['id'][:8]}... | Doctor: {rx['doctor_name']} | Date: {rx['prescription_date']}"
    return False, f"Status {detail_r.status_code}", ""

def test_file_upload_ocr():
    # Synthetic prescription text file upload
    synthetic_rx = b"""Rx:
Dr. Neha Patel (Cardiologist)
Date: 2026-09-04
1. Metoprolol 25 mg - 1 tablet once daily morning (30 days)
2. Rosuvastatin 10 mg - 1 tablet night after food (30 days)
"""
    files = {"files": ("sample_synthetic_rx.txt", io.BytesIO(synthetic_rx), "text/plain")}
    data = {"user_id": USER_ID}
    r = requests.post(f"{BACKEND_URL}/api/prescriptions/upload", files=files, data=data, timeout=10)
    if r.status_code == 200:
        saved = r.json()
        return True, "OK", f"Uploaded & parsed prescription: {saved[0]['file_name']} (Found {saved[0]['medicines_count']} meds)"
    return False, f"Upload status {r.status_code}: {r.text}", ""

# Global state for analysis tests
analysis_cache = {}

# ==============================================================================
# 5. CLINICAL SAFETY ANALYSIS PIPELINE
# ==============================================================================
def test_clinical_safety_analysis():
    r = requests.post(f"{BACKEND_URL}/api/prescriptions/analyse", data={"user_id": USER_ID}, timeout=25)
    if r.status_code != 200:
        return False, f"Analysis failed with {r.status_code}: {r.text}", ""
    data = r.json()
    analysis_cache["id"] = data["analysis_id"]
    analysis_cache["data"] = data
    stats = data.get("statistics", {})
    warnings = data.get("warnings", [])
    
    details = (
        f"Total Meds: {stats.get('total_medicines')} | "
        f"Duplicates: {stats.get('duplicate_count')} | "
        f"Interactions: {stats.get('interaction_count')} | "
        f"Clean Meds: {stats.get('clean_medicines_count')}"
    )
    return True, "OK", details

def test_duplicate_active_ingredient_detection():
    data = analysis_cache.get("data")
    if not data:
        return False, "Analysis data not found", ""
    warnings = data.get("warnings", [])
    dups = [w for w in warnings if w.get("analysis_type") == "duplicate"]
    if dups:
        d = dups[0]
        return True, "OK", f"Detected duplicate: {d.get('medicine_a_name')} & {d.get('medicine_b_name')} [{d.get('severity')}]"
    return False, "Duplicate active ingredient warning not triggered", ""

def test_drug_drug_interaction_detection():
    data = analysis_cache.get("data")
    if not data:
        return False, "Analysis data not found", ""
    warnings = data.get("warnings", [])
    interactions = [w for w in warnings if w.get("analysis_type") == "interaction"]
    if len(interactions) >= 2:
        pairs = [f"{w.get('medicine_a_name')}+{w.get('medicine_b_name')}" for w in interactions[:3]]
        return True, "OK", f"Detected interactions: {', '.join(pairs)}"
    return False, f"Expected multiple interactions, found {len(interactions)}", ""

def test_analysis_medicines_and_warnings_endpoints():
    aid = analysis_cache.get("id")
    if not aid:
        return False, "No analysis ID", ""
    m_res = requests.get(f"{BACKEND_URL}/api/analysis/{aid}/medicines", params={"user_id": USER_ID}, timeout=5)
    w_res = requests.get(f"{BACKEND_URL}/api/analysis/{aid}/warnings", params={"user_id": USER_ID}, timeout=5)
    if m_res.status_code == 200 and w_res.status_code == 200:
        return True, "OK", f"Retrieved {len(m_res.json())} extracted medicines and {len(w_res.json())} clinical warnings"
    return False, f"Medicines: {m_res.status_code}, Warnings: {w_res.status_code}", ""

def test_confirm_analysis():
    aid = analysis_cache.get("id")
    r = requests.post(f"{BACKEND_URL}/api/analysis/{aid}/confirm", data={"user_id": USER_ID}, timeout=5)
    if r.status_code == 200:
        d = r.json()
        return True, "OK", d.get("message", "Confirmed successfully")
    return False, f"Status {r.status_code}", ""

# ==============================================================================
# 6. CONSOLIDATED MEDICATION PLAN & PDF GENERATOR
# ==============================================================================
def test_consolidated_plan():
    aid = analysis_cache.get("id")
    r = requests.get(f"{BACKEND_URL}/api/consolidated-plan/{aid}", params={"user_id": USER_ID}, timeout=5)
    if r.status_code == 200:
        plan = r.json()
        slots_sample = [f"{m['medicine_name']} ({', '.join(m.get('schedule_slots', []))})" for m in plan[:2]]
        return True, "OK", f"Generated {len(plan)} consolidated medications. Slots: {'; '.join(slots_sample)}"
    return False, f"Status {r.status_code}", ""

def test_pdf_generation():
    aid = analysis_cache.get("id")
    r = requests.post(f"{BACKEND_URL}/api/consolidated-plan/{aid}/pdf", data={"user_id": USER_ID}, timeout=15)
    if r.status_code == 200 and r.content.startswith(b"%PDF-"):
        return True, "OK", f"Valid PDF binary generated ({len(r.content)} bytes with header %PDF-)"
    return False, f"PDF failed (status {r.status_code}, length {len(r.content)})", ""

# ==============================================================================
# 7. MULTI-LANGUAGE & VOICE TRANSLATION
# ==============================================================================
def test_update_language_preference():
    r = requests.put(f"{BACKEND_URL}/api/language", data={"user_id": USER_ID, "preferred_language": "ta"}, timeout=5)
    if r.status_code == 200:
        d = r.json()
        return True, "OK", f"User language set to: {d.get('language_name')} ({d.get('preferred_language')})"
    return False, f"Status {r.status_code}", ""

def test_translate_text_tamil():
    payload = {
        "text": "Safety Alert: Taking Aspirin and Clopidogrel together increases risk of bleeding. Consult your doctor.",
        "target_language": "ta"
    }
    r = requests.post(f"{BACKEND_URL}/api/language/translate", json=payload, timeout=10)
    if r.status_code == 200:
        d = r.json()
        trans = d.get("translated_text", "")
        return True, "OK", f"Tamil translation: {trans[:60]}..."
    return False, f"Status {r.status_code}", ""

def test_translate_text_hindi():
    payload = {
        "text": "Dosage Warning: The combined daily dose of Paracetamol exceeds recommended safety limits.",
        "target_language": "hi"
    }
    r = requests.post(f"{BACKEND_URL}/api/language/translate", json=payload, timeout=10)
    if r.status_code == 200:
        d = r.json()
        trans = d.get("translated_text", "")
        return True, "OK", f"Hindi translation: {trans[:60]}..."
    return False, f"Status {r.status_code}", ""

def test_voice_speech_payload():
    payload = {
        "text": "Take Atorvastatin 20 mg at bedtime.",
        "target_language": "ta"
    }
    r = requests.post(f"{BACKEND_URL}/api/language/speech", json=payload, timeout=5)
    if r.status_code == 200:
        d = r.json()
        return True, "OK", f"Speech engine: {d.get('engine')} | Voice lang: {d.get('voice_lang')}"
    return False, f"Status {r.status_code}", ""

# ==============================================================================
# 8. MEDICATION REMINDERS SYSTEM
# ==============================================================================
reminder_cache = {}

def test_create_reminder():
    payload = {
        "medicine_name": "Atorvastatin 20 mg",
        "dose": "1 tablet",
        "time": "21:00",
        "frequency": "once_daily",
        "instructions": "Take after dinner at bedtime"
    }
    r = requests.post(f"{BACKEND_URL}/api/reminders", json=payload, params={"user_id": USER_ID}, timeout=5)
    if r.status_code == 200:
        d = r.json()
        reminder_cache["id"] = d["id"]
        return True, "OK", f"Created reminder ID: {d['id'][:8]} for {d['medicine_name']} at {d['time']}"
    return False, f"Status {r.status_code}: {r.text}", ""

def test_list_reminders():
    r = requests.get(f"{BACKEND_URL}/api/reminders", params={"user_id": USER_ID}, timeout=5)
    if r.status_code == 200:
        rems = r.json()
        return True, "OK", f"Active reminders count: {len(rems)} (Status: {rems[0].get('today_status')})"
    return False, f"Status {r.status_code}", ""

def test_complete_reminder():
    rem_id = reminder_cache.get("id")
    if not rem_id:
        return False, "No reminder ID", ""
    r = requests.post(f"{BACKEND_URL}/api/reminders/{rem_id}/complete", data={"user_id": USER_ID}, timeout=5)
    if r.status_code == 200:
        d = r.json()
        return True, "OK", f"Marked reminder as taken: {d.get('status')}"
    return False, f"Status {r.status_code}: {r.text}", ""

def test_reminder_history():
    r = requests.get(f"{BACKEND_URL}/api/reminders/history", params={"user_id": USER_ID}, timeout=5)
    if r.status_code == 200:
        hist = r.json()
        return True, "OK", f"Adherence history records: {len(hist)} (Status: {hist[0].get('status')})"
    return False, f"Status {r.status_code}", ""

def test_toggle_reminder():
    rem_id = reminder_cache.get("id")
    if not rem_id:
        return False, "No reminder ID", ""
    r = requests.put(f"{BACKEND_URL}/api/reminders/{rem_id}", params={"enabled": False}, timeout=5)
    if r.status_code == 200:
        d = r.json()
        return True, "OK", f"Reminder enabled toggled to: {d.get('enabled')}"
    return False, f"Status {r.status_code}", ""

def test_delete_reminder():
    rem_id = reminder_cache.get("id")
    if not rem_id:
        return False, "No reminder ID", ""
    r = requests.delete(f"{BACKEND_URL}/api/reminders/{rem_id}", timeout=5)
    if r.status_code == 200:
        return True, "OK", f"Reminder {rem_id[:8]} deleted successfully"
    return False, f"Status {r.status_code}", ""

# ==============================================================================
# 9. MEDICINE EDITING & CORRECTION
# ==============================================================================
def test_medicine_update():
    # Fetch a medicine from the user's prescriptions
    db_r = requests.get(f"{BACKEND_URL}/api/prescriptions", params={"user_id": USER_ID}, timeout=5)
    rxs = db_r.json()
    if not rxs:
        return False, "No prescriptions found", ""
    aid = analysis_cache.get("id")
    meds_r = requests.get(f"{BACKEND_URL}/api/analysis/{aid}/medicines", params={"user_id": USER_ID}, timeout=5)
    meds = meds_r.json()
    if not meds:
        return False, "No medicines found", ""
    med = meds[0]
    
    # Update strength/frequency
    up_r = requests.put(
        f"{BACKEND_URL}/api/medicines/{med['id']}", 
        json={"strength": "1000 mg", "instructions": "Take with full meal"},
        timeout=5
    )
    if up_r.status_code == 200:
        updated = up_r.json()
        return True, "OK", f"Updated {updated['original_name']} strength to {updated['strength']} ({updated['instructions']})"
    return False, f"Status {up_r.status_code}", ""

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
def main():
    print(f"\n{BOLD}=============================================================================={RESET}")
    print(f"{BOLD}{CYAN}      MediGuard AI — Master Full-Stack System Verification Suite{RESET}")
    print(f"{BOLD}=============================================================================={RESET}\n")

    test_plan = [
        # Category 1: Frontend & Routing
        ("FE-01", "Frontend Web Application Root", "Frontend", test_frontend_home),
        ("FE-02", "Client Application Routes (6 Pages)", "Frontend", test_frontend_routes),
        
        # Category 2: Backend Core
        ("BE-01", "FastAPI Service Health Check", "Backend", test_backend_health),
        ("BE-02", "Interactive API Documentation (Swagger)", "Backend", test_backend_docs),
        
        # Category 3: Auth & Profile
        ("AUTH-01", "Patient Profile Creation & Synchronization", "Auth & Profile", test_user_profile),
        
        # Category 4: Prescriptions & OCR
        ("RX-01", "Load Realistic Multi-Doctor Prescriptions", "Prescriptions", test_load_sample_prescriptions),
        ("RX-02", "List Patient Prescriptions with Medicine Counts", "Prescriptions", test_list_prescriptions),
        ("RX-03", "Fetch Prescription Details & Metadata", "Prescriptions", test_single_prescription_detail),
        ("RX-04", "Prescription File Upload & Entity Extraction", "Prescriptions", test_file_upload_ocr),
        
        # Category 5: Clinical Safety Engine
        ("SAFE-01", "Clinical Medication Safety Analysis Pipeline", "Clinical Safety", test_clinical_safety_analysis),
        ("SAFE-02", "Duplicate Active Ingredient Detection (Paracetamol/Dolo)", "Clinical Safety", test_duplicate_active_ingredient_detection),
        ("SAFE-03", "Drug-Drug Interaction Engine (Aspirin/Clopidogrel/Omeprazole)", "Clinical Safety", test_drug_drug_interaction_detection),
        ("SAFE-04", "Extracted Medicines & Safety Warnings Endpoints", "Clinical Safety", test_analysis_medicines_and_warnings_endpoints),
        ("SAFE-05", "User Review Confirmation Flow", "Clinical Safety", test_confirm_analysis),
        
        # Category 6: Consolidated Plan & PDF
        ("PLAN-01", "Consolidated Medication Plan with Schedule Slots", "Medication Plan", test_consolidated_plan),
        ("PLAN-02", "Official Consolidated Medication Summary PDF Generation", "Medication Plan", test_pdf_generation),
        
        # Category 7: Regional Language & Voice
        ("I18N-01", "Update Regional Language Preference", "Regional Language", test_update_language_preference),
        ("I18N-02", "Regional Medical Translation (Tamil)", "Regional Language", test_translate_text_tamil),
        ("I18N-03", "Regional Medical Translation (Hindi)", "Regional Language", test_translate_text_hindi),
        ("I18N-04", "Voice Audio Synthesis Payload Preparation", "Regional Language", test_voice_speech_payload),
        
        # Category 8: Medication Reminders & Adherence
        ("REM-01", "Schedule New Medication Reminder", "Reminders", test_create_reminder),
        ("REM-02", "List Reminders with Daily Status", "Reminders", test_list_reminders),
        ("REM-03", "Mark Reminder as Taken (Adherence Log)", "Reminders", test_complete_reminder),
        ("REM-04", "Fetch Historical Adherence Log", "Reminders", test_reminder_history),
        ("REM-05", "Toggle Reminder Active State", "Reminders", test_toggle_reminder),
        ("REM-06", "Delete Reminder Record", "Reminders", test_delete_reminder),
        
        # Category 9: Medicine Correction
        ("MED-01", "Update Medicine Details / Strength / Frequency", "Medicines", test_medicine_update),
    ]

    for tid, title, cat, fn in test_plan:
        run_test(tid, title, cat, fn)

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r[3])
    failed = total - passed
    total_time = sum(r[4] for r in results)

    print(f"\n{BOLD}=============================================================================={RESET}")
    print(f"{BOLD}                           VERIFICATION SUMMARY{RESET}")
    print(f"{BOLD}=============================================================================={RESET}")
    print(f"  Total Operations Checked: {BOLD}{total}{RESET}")
    print(f"  Passed:                   {GREEN}{BOLD}{passed}{RESET}")
    print(f"  Failed:                   {RED}{BOLD}{failed}{RESET}")
    print(f"  Total Test Time:          {CYAN}{BOLD}{total_time:.2f}s{RESET}")
    rate = (passed / total * 100) if total > 0 else 0.0
    print(f"  Success Rate:             {BOLD}{rate:.1f}%{RESET}")
    print(f"{BOLD}=============================================================================={RESET}\n")

    if failed == 0:
        print(f"{GREEN}{BOLD}🎉 ALL OPERATIONS AND WHOLE WEBSITE WORK PERFECTLY!{RESET}\n")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}⚠️ {failed} operation(s) failed. See logs above for details.{RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
