import sys
import io
import time
import requests

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"
TEST_USER_ID = "test-patient-system-audit"

def log_test(name, passed, detail=""):
    symbol = "✅ PASS" if passed else "❌ FAIL"
    print(f"[{symbol}] {name} {f'-> {detail}' if detail else ''}")
    return passed

def run_tests():
    print("=" * 70)
    print("MediGuard AI: Full End-to-End System & API Verification Test Suite")
    print("=" * 70)
    
    passed_count = 0
    total_count = 0

    def assert_test(name, condition, detail=""):
        nonlocal passed_count, total_count
        total_count += 1
        if log_test(name, condition, detail):
            passed_count += 1
        else:
            print(f"   [ERROR TRACE] Condition failed: {detail}")

    # ==========================================
    # 1. FRONTEND SERVER ROUTE VERIFICATION
    # ==========================================
    print("\n--- Phase 1: Frontend Route Reachability (Port 5173) ---")
    frontend_routes = [
        "/",
        "/login",
        "/dashboard",
        "/prescriptions",
        "/analysis",
        "/medications",
        "/reminders",
        "/history",
        "/auth/callback"
    ]
    for route in frontend_routes:
        try:
            r = requests.get(f"{FRONTEND_URL}{route}", timeout=5)
            assert_test(f"Frontend route {route}", r.status_code == 200, f"Status: {r.status_code}")
        except Exception as e:
            assert_test(f"Frontend route {route}", False, str(e))

    # ==========================================
    # 2. BACKEND HEALTH & ROOT ENDPOINTS
    # ==========================================
    print("\n--- Phase 2: Backend Core Health & Docs (Port 8000) ---")
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=5)
        data = r.json()
        assert_test("Backend /health", r.status_code == 200 and data.get("status") == "healthy", f"Status: {data.get('status')}")
    except Exception as e:
        assert_test("Backend /health", False, str(e))

    try:
        r = requests.get(f"{BACKEND_URL}/", timeout=5)
        data = r.json()
        assert_test("Backend / root message", r.status_code == 200 and "MediGuard AI" in data.get("message", ""), data.get("message"))
    except Exception as e:
        assert_test("Backend / root message", False, str(e))

    try:
        r = requests.get(f"{BACKEND_URL}/docs", timeout=5)
        assert_test("Backend /docs Swagger UI", r.status_code == 200, f"Status: {r.status_code}")
    except Exception as e:
        assert_test("Backend /docs Swagger UI", False, str(e))

    # ==========================================
    # 3. SUPABASE USER PROFILE & LANGUAGE PREFERENCES
    # ==========================================
    print("\n--- Phase 3: Supabase User Profile & Language API ---")
    try:
        profile_payload = {
            "user_id": TEST_USER_ID,
            "full_name": "Dr. System Tester",
            "email": "audit@mediguard.ai",
            "avatar_url": "https://api.dicebear.com/7.x/initials/svg?seed=Audit",
            "preferred_language": "en"
        }
        r = requests.post(f"{BACKEND_URL}/api/auth/profile", json=profile_payload, timeout=8)
        assert_test("POST /api/auth/profile", r.status_code == 200, f"Status: {r.status_code} {r.text if r.status_code != 200 else ''}")
    except Exception as e:
        assert_test("POST /api/auth/profile", False, str(e))

    try:
        r = requests.get(f"{BACKEND_URL}/api/auth/profile/{TEST_USER_ID}", timeout=8)
        data = r.json() if r.status_code == 200 else {}
        assert_test("GET /api/auth/profile/{id}", r.status_code == 200 and data.get("email") == "audit@mediguard.ai", f"Full name: {data.get('full_name')}")
    except Exception as e:
        assert_test("GET /api/auth/profile/{id}", False, str(e))

    try:
        r = requests.put(f"{BACKEND_URL}/api/language", data={"user_id": TEST_USER_ID, "preferred_language": "ta"}, timeout=8)
        data = r.json() if r.status_code == 200 else {}
        assert_test("PUT /api/language (set Tamil 'ta')", r.status_code == 200 and data.get("preferred_language") == "ta", f"Language: {data.get('language_name')} {r.text if r.status_code != 200 else ''}")
    except Exception as e:
        assert_test("PUT /api/language", False, str(e))

    # ==========================================
    # 4. LOAD SAMPLE MULTI-DOCTOR PRESCRIPTIONS
    # ==========================================
    print("\n--- Phase 4: Multi-Doctor Sample Prescriptions Ingestion ---")
    try:
        r = requests.post(f"{BACKEND_URL}/api/prescriptions/load-sample-prescriptions", data={"user_id": TEST_USER_ID}, timeout=15)
        assert_test("POST /api/prescriptions/load-sample-prescriptions", r.status_code == 200 and r.json().get("count") == 3, f"Count: {r.json().get('count')}")
    except Exception as e:
        assert_test("POST /api/prescriptions/load-sample-prescriptions", False, str(e))

    rx_list = []
    try:
        r = requests.get(f"{BACKEND_URL}/api/prescriptions", params={"user_id": TEST_USER_ID}, timeout=8)
        rx_list = r.json()
        assert_test("GET /api/prescriptions", r.status_code == 200 and len(rx_list) == 3, f"Prescriptions retrieved: {len(rx_list)}")
    except Exception as e:
        assert_test("GET /api/prescriptions", False, str(e))

    if rx_list:
        try:
            rx_id = rx_list[0]["id"]
            r = requests.get(f"{BACKEND_URL}/api/prescriptions/{rx_id}", timeout=8)
            assert_test("GET /api/prescriptions/{id}", r.status_code == 200, f"Doctor: {r.json().get('doctor_name')}")
        except Exception as e:
            assert_test("GET /api/prescriptions/{id}", False, str(e))

    # ==========================================
    # 5. CLINICAL SAFETY & MULTI-PRESCRIPTION ANALYSIS ENGINE
    # ==========================================
    print("\n--- Phase 5: Multi-Prescription Clinical Safety Engine ---")
    analysis_res = None
    try:
        r = requests.post(f"{BACKEND_URL}/api/prescriptions/analyse", data={"user_id": TEST_USER_ID}, timeout=25)
        analysis_res = r.json() if r.status_code == 200 else {}
        assert_test("POST /api/prescriptions/analyse", r.status_code == 200, f"Analysis ID: {analysis_res.get('analysis_id')} {r.text if r.status_code != 200 else ''}")
    except Exception as e:
        assert_test("POST /api/prescriptions/analyse", False, str(e))

    if analysis_res:
        stats = analysis_res.get("statistics", {})
        warnings = analysis_res.get("warnings", [])
        plan = analysis_res.get("consolidated_plan", [])
        
        # Test duplicate detection
        dup_warnings = [w for w in warnings if w.get("analysis_type") == "duplicate"]
        assert_test("Duplicate / Overlap Detection (Dolo 650 & Paracetamol)", len(dup_warnings) > 0, f"Duplicates found: {len(dup_warnings)}")

        # Test drug-drug interaction detection
        inter_warnings = [w for w in warnings if w.get("analysis_type") == "interaction"]
        assert_test("Drug-Drug Interaction Detection (Aspirin + Ibuprofen / Clopidogrel + Omeprazole)", len(inter_warnings) >= 2, f"Interactions found: {len(inter_warnings)}")

        # Test dosage concern detection
        dose_warnings = [w for w in warnings if w.get("analysis_type") == "dosage_concern"]
        assert_test("Cumulative Dosage Threshold Alerts", len(dose_warnings) > 0, f"Dosage warnings: {len(dose_warnings)}")

        # Test consolidated plan generation
        assert_test("Consolidated Medication Review Plan", len(plan) > 0, f"Plan items: {len(plan)}")

        analysis_id = analysis_res.get("analysis_id")
        
        # Test sub-endpoints
        try:
            r = requests.get(f"{BACKEND_URL}/api/analysis/{analysis_id}/medicines", params={"user_id": TEST_USER_ID}, timeout=5)
            assert_test("GET /api/analysis/{id}/medicines", r.status_code == 200 and len(r.json()) > 0, f"Medicines: {len(r.json())}")
        except Exception as e:
            assert_test("GET /api/analysis/{id}/medicines", False, str(e))

        try:
            r = requests.get(f"{BACKEND_URL}/api/analysis/{analysis_id}/warnings", params={"user_id": TEST_USER_ID}, timeout=5)
            assert_test("GET /api/analysis/{id}/warnings", r.status_code == 200 and len(r.json()) > 0, f"Warnings: {len(r.json())}")
        except Exception as e:
            assert_test("GET /api/analysis/{id}/warnings", False, str(e))

        try:
            r = requests.get(f"{BACKEND_URL}/api/consolidated-plan/{analysis_id}", params={"user_id": TEST_USER_ID}, timeout=5)
            assert_test("GET /api/consolidated-plan/{id}", r.status_code == 200 and len(r.json()) > 0, f"Consolidated items: {len(r.json())}")
        except Exception as e:
            assert_test("GET /api/consolidated-plan/{id}", False, str(e))

    # ==========================================
    # 6. USER ANALYSIS CONFIRMATION (STEP 9/10)
    # ==========================================
    print("\n--- Phase 6: User Analysis Confirmation ---")
    if analysis_res:
        analysis_id = analysis_res.get("analysis_id")
        try:
            r = requests.post(f"{BACKEND_URL}/api/analysis/{analysis_id}/confirm", data={"user_id": TEST_USER_ID}, timeout=5)
            assert_test("POST /api/analysis/{id}/confirm", r.status_code == 200, r.json().get("message"))
        except Exception as e:
            assert_test("POST /api/analysis/{id}/confirm", False, str(e))

    # ==========================================
    # 7. CONSOLIDATED MEDICATION SUMMARY PDF GENERATION
    # ==========================================
    print("\n--- Phase 7: PDF Generation Service ---")
    if analysis_res:
        analysis_id = analysis_res.get("analysis_id")
        try:
            r = requests.post(f"{BACKEND_URL}/api/consolidated-plan/{analysis_id}/pdf", data={"user_id": TEST_USER_ID}, timeout=10)
            is_pdf = r.status_code == 200 and r.content.startswith(b"%PDF-")
            assert_test("POST /api/consolidated-plan/{id}/pdf", is_pdf, f"Bytes: {len(r.content)}, Content-Type: {r.headers.get('content-type')}")
        except Exception as e:
            assert_test("POST /api/consolidated-plan/{id}/pdf", False, str(e))

    # ==========================================
    # 8. REGIONAL TRANSLATION & VOICE SYNTHESIS
    # ==========================================
    print("\n--- Phase 8: Regional Language Translation & Speech Synthesis ---")
    try:
        trans_payload = {
            "text": "Take one tablet daily after meals",
            "target_language": "ta"
        }
        r = requests.post(f"{BACKEND_URL}/api/language/translate", json=trans_payload, timeout=5)
        translated = r.json().get("translated_text", "")
        assert_test("POST /api/language/translate (Tamil)", r.status_code == 200 and len(translated) > 0, f"Result: {translated}")
    except Exception as e:
        assert_test("POST /api/language/translate", False, str(e))

    try:
        speech_payload = {
            "text": "Warning: High risk of bleeding when taking Aspirin and Ibuprofen together.",
            "target_language": "ta"
        }
        r = requests.post(f"{BACKEND_URL}/api/language/speech", json=speech_payload, timeout=10)
        data = r.json()
        has_audio = r.status_code == 200 and data.get("has_audio") is True and len(data.get("audio_base64", "")) > 100
        assert_test("POST /api/language/speech (MP3 audio generation)", has_audio, f"Has Audio: {data.get('has_audio')}, Format: {data.get('audio_format')}")
    except Exception as e:
        assert_test("POST /api/language/speech", False, str(e))

    try:
        r = requests.get(f"{BACKEND_URL}/api/language/audio", params={"text": "MediGuard AI active", "lang": "en"}, timeout=5)
        assert_test("GET /api/language/audio (Direct binary audio stream)", r.status_code == 200 and len(r.content) > 100, f"Audio bytes: {len(r.content)}")
    except Exception as e:
        assert_test("GET /api/language/audio", False, str(e))

    # ==========================================
    # 9. MEDICATION REMINDERS & ADHERENCE LOGGING
    # ==========================================
    print("\n--- Phase 9: Medication Reminders & Adherence History ---")
    rem_id = None
    try:
        reminder_payload = {
            "medicine_name": "Atorvastatin 20 mg",
            "dose": "1 tablet",
            "time": "08:00 AM",
            "frequency": "once_daily",
            "instructions": "Take at bedtime with water"
        }
        r = requests.post(f"{BACKEND_URL}/api/reminders", json=reminder_payload, params={"user_id": TEST_USER_ID}, timeout=5)
        rem_data = r.json()
        rem_id = rem_data.get("id")
        assert_test("POST /api/reminders (Create reminder)", r.status_code == 200 and rem_id is not None, f"Reminder ID: {rem_id}")
    except Exception as e:
        assert_test("POST /api/reminders", False, str(e))

    try:
        r = requests.get(f"{BACKEND_URL}/api/reminders", params={"user_id": TEST_USER_ID}, timeout=5)
        rems = r.json()
        assert_test("GET /api/reminders", r.status_code == 200 and len(rems) > 0, f"Active reminders: {len(rems)}")
    except Exception as e:
        assert_test("GET /api/reminders", False, str(e))

    if rem_id:
        try:
            r = requests.put(f"{BACKEND_URL}/api/reminders/{rem_id}", params={"enabled": False}, timeout=5)
            assert_test("PUT /api/reminders/{id} (Toggle disabled)", r.status_code == 200 and r.json().get("enabled") is False, f"Enabled: {r.json().get('enabled')}")
        except Exception as e:
            assert_test("PUT /api/reminders/{id} (Disable)", False, str(e))

        try:
            r = requests.put(f"{BACKEND_URL}/api/reminders/{rem_id}", params={"enabled": True}, timeout=5)
            assert_test("PUT /api/reminders/{id} (Toggle re-enabled)", r.status_code == 200 and r.json().get("enabled") is True, f"Enabled: {r.json().get('enabled')}")
        except Exception as e:
            assert_test("PUT /api/reminders/{id} (Enable)", False, str(e))

        try:
            r = requests.post(f"{BACKEND_URL}/api/reminders/{rem_id}/complete", data={"user_id": TEST_USER_ID}, timeout=5)
            assert_test("POST /api/reminders/{id}/complete (Record Taken)", r.status_code == 200 and r.json().get("status") == "taken", r.json().get("message"))
        except Exception as e:
            assert_test("POST /api/reminders/{id}/complete", False, str(e))

        try:
            r = requests.get(f"{BACKEND_URL}/api/reminders/history", params={"user_id": TEST_USER_ID}, timeout=5)
            history = r.json()
            assert_test("GET /api/reminders/history (Adherence audit trail)", r.status_code == 200 and len(history) > 0, f"History records: {len(history)}")
        except Exception as e:
            assert_test("GET /api/reminders/history", False, str(e))

        try:
            r = requests.delete(f"{BACKEND_URL}/api/reminders/{rem_id}", timeout=5)
            assert_test("DELETE /api/reminders/{id}", r.status_code == 200, r.json().get("message"))
        except Exception as e:
            assert_test("DELETE /api/reminders/{id}", False, str(e))

    # ==========================================
    # 10. MEDICINE EDITING & VERIFICATION CORRECTION
    # ==========================================
    print("\n--- Phase 10: Medicine Correction & Editing ---")
    try:
        # Get one medicine from analysis
        r = requests.get(f"{BACKEND_URL}/api/prescriptions", params={"user_id": TEST_USER_ID}, timeout=5)
        rx_rows = r.json()
        if rx_rows:
            med_list = requests.get(f"{BACKEND_URL}/api/analysis/{analysis_id}/medicines", params={"user_id": TEST_USER_ID}, timeout=5).json()
            if med_list:
                med = med_list[0]
                med_id = med["id"]
                update_payload = {
                    "strength": "40 mg",
                    "instructions": "Take strictly after dinner"
                }
                up_res = requests.put(f"{BACKEND_URL}/api/medicines/{med_id}", json=update_payload, timeout=10)
                assert_test("PUT /api/medicines/{id} (Edit strength/instructions)", up_res.status_code == 200 and up_res.json().get("strength") == "40 mg", f"Updated strength: {up_res.json().get('strength')}")
    except Exception as e:
        assert_test("PUT /api/medicines/{id}", False, str(e))

    # ==========================================
    # 11. FILE UPLOAD TEST (SYNTHETIC PRESCRIPTION)
    # ==========================================
    print("\n--- Phase 11: Real File Upload Pipeline ---")
    try:
        prescription_sample_text = (
            "DR. RAJESH SHARMA, MD\n"
            "Apollo Hospital, Bengaluru\n"
            "Date: 2026-09-10\n"
            "Patient: System Audit Test\n\n"
            "Rx:\n"
            "1. Metformin 500 mg - 1 tab twice daily with meals (60 days)\n"
            "2. Glimepiride 1 mg - 1 tab once daily before breakfast (30 days)\n"
        )
        fake_file = io.BytesIO(prescription_sample_text.encode('utf-8'))
        files = [('files', ('test_rx.txt', fake_file, 'text/plain'))]
        data = {'user_id': TEST_USER_ID}
        r = requests.post(f"{BACKEND_URL}/api/prescriptions/upload", data=data, files=files, timeout=10)
        uploaded = r.json()
        assert_test("POST /api/prescriptions/upload (File ingestion & extraction)", r.status_code == 200 and len(uploaded) > 0, f"Saved prescriptions: {len(uploaded)}")
    except Exception as e:
        assert_test("POST /api/prescriptions/upload", False, str(e))

    # ==========================================
    # SUMMARY
    # ==========================================
    print("\n" + "=" * 70)
    success_rate = (passed_count / total_count * 100) if total_count > 0 else 0.0
    print(f"TEST SUMMARY: {passed_count} / {total_count} PASSED ({success_rate:.1f}%)")
    print("=" * 70)

    if passed_count == total_count:
        print("🎉 ALL TESTS PASSED! FULL SYSTEM IS FULLY FUNCTIONAL AND ERROR-FREE.")
        return 0
    else:
        print(f"⚠️ {total_count - passed_count} TESTS FAILED. PLEASE INVESTIGATE TRACES ABOVE.")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
