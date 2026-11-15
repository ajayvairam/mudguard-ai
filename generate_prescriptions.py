import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = Path(r"c:\Users\ajayv\OneDrive\Desktop\mediguardai")
BACKEND_SAMPLES = OUTPUT_DIR / "backend" / "samples"
FRONTEND_SAMPLES = OUTPUT_DIR / "frontend" / "public" / "samples"
BACKEND_SAMPLES.mkdir(parents=True, exist_ok=True)
FRONTEND_SAMPLES.mkdir(parents=True, exist_ok=True)

# Try system fonts with fallbacks
def get_font(font_name, size, bold=False):
    win_fonts = Path(r"C:\Windows\Fonts")
    if bold:
        candidates = [
            win_fonts / f"{font_name}bd.ttf",
            win_fonts / f"{font_name}b.ttf",
            win_fonts / "arialbd.ttf",
            win_fonts / "segoeuib.ttf",
        ]
    else:
        candidates = [
            win_fonts / f"{font_name}.ttf",
            win_fonts / "arial.ttf",
            win_fonts / "segoeui.ttf",
        ]
    for p in candidates:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_round_stamp(draw, center_x, center_y, radius, text_top, text_bottom, text_center, color=(40, 50, 160, 180)):
    # Draw outer circles
    for r in [radius, radius - 4, radius - 16, radius - 18]:
        draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], outline=color, width=2)
    
    font_sm = get_font("arial", 20, bold=True)
    font_center = get_font("arial", 24, bold=True)
    
    # Draw center text
    bbox = draw.textbbox((0, 0), text_center, font=font_center)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((center_x - w / 2, center_y - h / 2), text_center, fill=color, font=font_center)

    # Simple curved effect / text placement
    bbox_top = draw.textbbox((0, 0), text_top, font=font_sm)
    draw.text((center_x - (bbox_top[2] - bbox_top[0]) / 2, center_y - radius + 22), text_top, fill=color, font=font_sm)
    
    bbox_bot = draw.textbbox((0, 0), text_bottom, font=font_sm)
    draw.text((center_x - (bbox_bot[2] - bbox_bot[0]) / 2, center_y + radius - 40), text_bottom, fill=color, font=font_sm)

def draw_signature(draw, start_x, start_y, color=(25, 45, 140)):
    # Draw simulated physician cursive pen stroke
    points = [
        (start_x, start_y + 20),
        (start_x + 30, start_y - 25),
        (start_x + 50, start_y + 15),
        (start_x + 75, start_y - 15),
        (start_x + 95, start_y + 10),
        (start_x + 130, start_y - 30),
        (start_x + 150, start_y + 25),
        (start_x + 220, start_y - 5),
    ]
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=color, width=4)
    # Underline flourish
    flourish = [
        (start_x - 10, start_y + 35),
        (start_x + 100, start_y + 40),
        (start_x + 230, start_y + 32)
    ]
    for i in range(len(flourish) - 1):
        draw.line([flourish[i], flourish[i+1]], fill=color, width=3)

# ----------------------------------------------------------------------
# Prescription 1: Cardiology (Dr. A. Kumar)
# ----------------------------------------------------------------------
def generate_cardiology_rx():
    w, h = 1600, 2200
    # Create textured paper background (warm off-white clinical stationery)
    img = Image.new("RGB", (w, h), (252, 252, 250))
    draw = ImageDraw.Draw(img)

    # Subtle margin border
    draw.rectangle([50, 50, w - 50, h - 50], outline=(220, 225, 230), width=2)
    
    # Header Hospital / Clinic Branding
    # Teal/Navy medical theme
    PRIMARY_COLOR = (12, 74, 96)
    ACCENT_COLOR = (14, 116, 144)
    TEXT_COLOR = (30, 41, 59)
    LIGHT_TEXT = (100, 116, 139)

    # Clinic Logo Banner
    draw.rectangle([50, 50, w - 50, 260], fill=(240, 249, 255))
    draw.line([50, 260, w - 50, 260], fill=ACCENT_COLOR, width=4)

    # Hospital Emblem cross
    draw.rectangle([90, 85, 170, 165], fill=ACCENT_COLOR)
    draw.rectangle([115, 65, 145, 185], fill=ACCENT_COLOR)
    draw.rectangle([105, 100, 155, 150], fill=(255, 255, 255))

    # Doctor / Clinic Title
    draw.text((210, 75), "METRO HEART INSTITUTE & RESEARCH CENTRE", fill=PRIMARY_COLOR, font=get_font("arial", 42, bold=True))
    draw.text((210, 130), "Dr. A. Kumar, MBBS, MD, DM (Cardiology)", fill=TEXT_COLOR, font=get_font("arial", 32, bold=True))
    draw.text((210, 175), "Senior Interventional Cardiologist  |  Reg. No: TNMC-54921", fill=ACCENT_COLOR, font=get_font("arial", 24, bold=True))
    draw.text((210, 210), "124, Anna Salai, Chennai - 600002  |  Ph: +91 44 2855 4321  |  Email: cardiology@metroheart.in", fill=LIGHT_TEXT, font=get_font("arial", 20))

    # Patient Details Strip
    draw.rectangle([70, 280, w - 70, 390], fill=(248, 250, 252), outline=(226, 232, 240), width=2)
    
    draw.text((100, 300), "Patient Name:", fill=LIGHT_TEXT, font=get_font("arial", 22, bold=True))
    draw.text((260, 300), "Mr. Ramesh Sharma", fill=TEXT_COLOR, font=get_font("arial", 24, bold=True))

    draw.text((700, 300), "Age / Gender:", fill=LIGHT_TEXT, font=get_font("arial", 22, bold=True))
    draw.text((860, 300), "58 Yrs / Male", fill=TEXT_COLOR, font=get_font("arial", 24, bold=True))

    draw.text((1180, 300), "Date:", fill=LIGHT_TEXT, font=get_font("arial", 22, bold=True))
    draw.text((1250, 300), "15-Aug-2026", fill=TEXT_COLOR, font=get_font("arial", 24, bold=True))

    draw.text((100, 345), "Vitals / Notes:", fill=LIGHT_TEXT, font=get_font("arial", 22, bold=True))
    draw.text((260, 345), "BP: 138/88 mmHg  |  Pulse: 74 bpm  |  SpO2: 98%  |  Post-PCI Review (CAD)", fill=TEXT_COLOR, font=get_font("arial", 22))

    # Rx Symbol
    rx_font = get_font("times", 84, bold=True)
    draw.text((90, 420), "℞", fill=PRIMARY_COLOR, font=rx_font)
    draw.line([90, 520, w - 90, 520], fill=(226, 232, 240), width=2)

    # Prescription Medicines Block
    meds_start_y = 560
    
    medications = [
        {
            "num": "1.",
            "name": "Tab. Atorvastatin 20 mg",
            "dose": "1 tablet at bedtime (after food)",
            "duration": "Duration: 30 Days (1-0-0-1 Night)",
            "purpose": "For cholesterol management & plaque stabilization"
        },
        {
            "num": "2.",
            "name": "Tab. Clopidogrel 75 mg (Plavix)",
            "dose": "1 tablet once daily in the morning after breakfast",
            "duration": "Duration: 30 Days (1-0-0)",
            "purpose": "Antiplatelet therapy"
        },
        {
            "num": "3.",
            "name": "Tab. Aspirin 75 mg (Ecosprin 75)",
            "dose": "1 tablet once daily after lunch with a full glass of water",
            "duration": "Duration: 30 Days (0-1-0)",
            "purpose": "Cardioprotective antiplatelet"
        }
    ]

    curr_y = meds_start_y
    for med in medications:
        # Number and Medicine Name
        draw.text((110, curr_y), med["num"], fill=PRIMARY_COLOR, font=get_font("arial", 32, bold=True))
        draw.text((160, curr_y), med["name"], fill=(15, 23, 42), font=get_font("arial", 34, bold=True))
        
        # Dosage & Schedule
        curr_y += 50
        draw.text((160, curr_y), "• Dosage: " + med["dose"], fill=(51, 65, 85), font=get_font("arial", 26))
        
        curr_y += 40
        draw.text((160, curr_y), "• Schedule: " + med["duration"], fill=ACCENT_COLOR, font=get_font("arial", 24, bold=True))
        
        curr_y += 35
        draw.text((160, curr_y), "  Note: " + med["purpose"], fill=LIGHT_TEXT, font=get_font("arial", 22))

        curr_y += 65
        draw.line([160, curr_y, w - 120, curr_y], fill=(241, 245, 249), width=2)
        curr_y += 35

    # Clinical Advice Box
    curr_y += 40
    draw.rectangle([100, curr_y, w - 100, curr_y + 190], fill=(255, 251, 235), outline=(252, 211, 77), width=2)
    draw.text((130, curr_y + 20), "CLINICAL ADVICE & LIFESTYLE:", fill=(146, 64, 14), font=get_font("arial", 24, bold=True))
    draw.text((130, curr_y + 65), "1. Low salt (< 5g/day), low saturated fat diet. Avoid smoking & alcohol.", fill=(120, 53, 15), font=get_font("arial", 22))
    draw.text((130, curr_y + 105), "2. 30 mins brisk walking daily. Monitor home blood pressure twice weekly.", fill=(120, 53, 15), font=get_font("arial", 22))
    draw.text((130, curr_y + 145), "3. DO NOT discontinue antiplatelet therapy without consulting cardiologist.", fill=(180, 20, 20), font=get_font("arial", 22, bold=True))

    # Doctor Stamp & Signature Footer
    curr_y += 260
    draw_round_stamp(draw, 360, curr_y + 80, 110, "METRO HEART INSTITUTE", "CHENNAI - 600002", "VERIFIED Rx", color=(30, 64, 175, 200))

    # Doctor signature
    draw_signature(draw, w - 460, curr_y + 60, color=(15, 23, 140))
    draw.text((w - 470, curr_y + 120), "Dr. A. Kumar, MD, DM", fill=TEXT_COLOR, font=get_font("arial", 26, bold=True))
    draw.text((w - 470, curr_y + 155), "Reg No: TNMC-54921", fill=LIGHT_TEXT, font=get_font("arial", 22))
    draw.text((w - 470, curr_y + 185), "Senior Cardiologist", fill=LIGHT_TEXT, font=get_font("arial", 20))

    # Bottom legal footer
    draw.line([50, h - 110, w - 50, h - 110], fill=(203, 213, 225), width=2)
    draw.text((w / 2 - 380, h - 80), "Review after 30 days with Lipid Profile & ECG. For emergencies call +91 44 2855 4999", fill=LIGHT_TEXT, font=get_font("arial", 19))

    out_path = OUTPUT_DIR / "prescription_1_cardiology.png"
    img.save(out_path, "PNG", quality=95)
    img.save(BACKEND_SAMPLES / "dr_kumar_rx.png", "PNG", quality=95)
    img.save(FRONTEND_SAMPLES / "dr_kumar_rx.png", "PNG", quality=95)
    print(f"Saved Cardiology Prescription: {out_path}")

# ----------------------------------------------------------------------
# Prescription 2: Orthopedics (Dr. Priya Nair)
# ----------------------------------------------------------------------
def generate_orthopedics_rx():
    w, h = 1600, 2200
    img = Image.new("RGB", (w, h), (254, 253, 250))
    draw = ImageDraw.Draw(img)

    draw.rectangle([50, 50, w - 50, h - 50], outline=(225, 220, 225), width=2)

    PRIMARY_COLOR = (131, 24, 67) # Deep Rose/Burgundy for Orthopedics
    ACCENT_COLOR = (190, 24, 93)
    TEXT_COLOR = (30, 41, 59)
    LIGHT_TEXT = (100, 116, 139)

    # Hospital Header
    draw.rectangle([50, 50, w - 50, 260], fill=(253, 242, 248))
    draw.line([50, 260, w - 50, 260], fill=ACCENT_COLOR, width=4)

    # Medical cross in badge
    draw.ellipse([90, 85, 175, 170], fill=ACCENT_COLOR)
    draw.rectangle([122, 95, 142, 160], fill=(255, 255, 255))
    draw.rectangle([107, 117, 157, 138], fill=(255, 255, 255))

    draw.text((210, 75), "CITY BONE & JOINT SPECIALTY HOSPITAL", fill=PRIMARY_COLOR, font=get_font("arial", 42, bold=True))
    draw.text((210, 130), "Dr. Priya Nair, MBBS, MS (Ortho), DNB (Ortho)", fill=TEXT_COLOR, font=get_font("arial", 32, bold=True))
    draw.text((210, 175), "Consultant Orthopedic & Arthroscopy Surgeon  |  Reg. No: KMC-38410", fill=ACCENT_COLOR, font=get_font("arial", 24, bold=True))
    draw.text((210, 210), "78, Church Street, MG Road, Bengaluru - 560001  |  Ph: +91 80 4112 8899", fill=LIGHT_TEXT, font=get_font("arial", 20))

    # Patient Details Strip
    draw.rectangle([70, 280, w - 70, 390], fill=(248, 250, 252), outline=(226, 232, 240), width=2)
    
    draw.text((100, 300), "Patient Name:", fill=LIGHT_TEXT, font=get_font("arial", 22, bold=True))
    draw.text((260, 300), "Mr. Ramesh Sharma", fill=TEXT_COLOR, font=get_font("arial", 24, bold=True))

    draw.text((700, 300), "Age / Gender:", fill=LIGHT_TEXT, font=get_font("arial", 22, bold=True))
    draw.text((860, 300), "58 Yrs / Male", fill=TEXT_COLOR, font=get_font("arial", 24, bold=True))

    draw.text((1180, 300), "Date:", fill=LIGHT_TEXT, font=get_font("arial", 22, bold=True))
    draw.text((1250, 300), "01-Sep-2026", fill=TEXT_COLOR, font=get_font("arial", 24, bold=True))

    draw.text((100, 345), "Clinical Diagnosis:", fill=LIGHT_TEXT, font=get_font("arial", 22, bold=True))
    draw.text((310, 345), "Bilateral Knee Osteoarthritis (Grade II) + Acute Left Knee Joint Pain", fill=(185, 28, 28), font=get_font("arial", 22, bold=True))

    # Rx Symbol
    rx_font = get_font("times", 84, bold=True)
    draw.text((90, 420), "℞", fill=PRIMARY_COLOR, font=rx_font)
    draw.line([90, 520, w - 90, 520], fill=(226, 232, 240), width=2)

    # Prescription Medicines Block
    curr_y = 560
    
    ortho_medications = [
        {
            "num": "1.",
            "name": "Tab. Ibuprofen 400 mg (Brufen)",
            "dose": "1 tablet twice daily after meals (morning & night)",
            "duration": "Duration: 10 Days (1-0-1)",
            "purpose": "For acute joint pain & anti-inflammatory relief"
        },
        {
            "num": "2.",
            "name": "Tab. Dolo 650 (Paracetamol 650 mg)",
            "dose": "1 tablet three times daily after food (SOS for pain)",
            "duration": "Duration: 5 Days (1-1-1)",
            "purpose": "Analgesic for breakthrough body pain"
        },
        {
            "num": "3.",
            "name": "Cap. Pantoprazole 40 mg (Pan 40)",
            "dose": "1 capsule once daily in the morning on empty stomach (30 mins before food)",
            "duration": "Duration: 10 Days (1-0-0 Empty Stomach)",
            "purpose": "Gastric mucosal protection during NSAID therapy"
        }
    ]

    for med in ortho_medications:
        draw.text((110, curr_y), med["num"], fill=PRIMARY_COLOR, font=get_font("arial", 32, bold=True))
        draw.text((160, curr_y), med["name"], fill=(15, 23, 42), font=get_font("arial", 34, bold=True))
        
        curr_y += 50
        draw.text((160, curr_y), "• Dosage: " + med["dose"], fill=(51, 65, 85), font=get_font("arial", 26))
        
        curr_y += 40
        draw.text((160, curr_y), "• Schedule: " + med["duration"], fill=ACCENT_COLOR, font=get_font("arial", 24, bold=True))
        
        curr_y += 35
        draw.text((160, curr_y), "  Note: " + med["purpose"], fill=LIGHT_TEXT, font=get_font("arial", 22))

        curr_y += 65
        draw.line([160, curr_y, w - 120, curr_y], fill=(241, 245, 249), width=2)
        curr_y += 35

    # Physical Therapy & Precautions Box
    curr_y += 40
    draw.rectangle([100, curr_y, w - 100, curr_y + 190], fill=(254, 242, 242), outline=(252, 165, 165), width=2)
    draw.text((130, curr_y + 20), "ORTHOPEDIC INSTRUCTIONS & PRECAUTIONS:", fill=(153, 27, 27), font=get_font("arial", 24, bold=True))
    draw.text((130, curr_y + 65), "1. Apply warm compress to knee joint for 15 minutes twice daily.", fill=(127, 29, 29), font=get_font("arial", 22))
    draw.text((130, curr_y + 105), "2. Quadriceps isometric strengthening exercises as taught by physiotherapist.", fill=(127, 29, 29), font=get_font("arial", 22))
    draw.text((130, curr_y + 145), "3. Avoid cross-legged sitting and deep squatting. Use knee support while walking.", fill=(127, 29, 29), font=get_font("arial", 22))

    # Doctor Stamp & Signature Footer
    curr_y += 260
    draw_round_stamp(draw, 360, curr_y + 80, 110, "CITY BONE HOSPITAL", "BENGALURU - 560001", "ORTHO OPD", color=(159, 18, 57, 200))

    # Doctor signature
    draw_signature(draw, w - 460, curr_y + 60, color=(120, 20, 80))
    draw.text((w - 470, curr_y + 120), "Dr. Priya Nair, MS (Ortho)", fill=TEXT_COLOR, font=get_font("arial", 26, bold=True))
    draw.text((w - 470, curr_y + 155), "Reg No: KMC-38410", fill=LIGHT_TEXT, font=get_font("arial", 22))
    draw.text((w - 470, curr_y + 185), "Department of Orthopedics", fill=LIGHT_TEXT, font=get_font("arial", 20))

    # Bottom legal footer
    draw.line([50, h - 110, w - 50, h - 110], fill=(203, 213, 225), width=2)
    draw.text((w / 2 - 350, h - 80), "Follow-up after 10 days with repeat X-Ray Knee AP/Lateral view if pain persists.", fill=LIGHT_TEXT, font=get_font("arial", 19))

    out_path = OUTPUT_DIR / "prescription_2_orthopedics.png"
    img.save(out_path, "PNG", quality=95)
    img.save(BACKEND_SAMPLES / "dr_priya_rx.png", "PNG", quality=95)
    img.save(FRONTEND_SAMPLES / "dr_priya_rx.png", "PNG", quality=95)
    print(f"Saved Orthopedics Prescription: {out_path}")

if __name__ == "__main__":
    generate_cardiology_rx()
    generate_orthopedics_rx()
    print("Both prescription photos generated successfully!")
