import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from config import SAMPLES_DIR

def create_prescription_image(filename: str, doctor: str, specialty: str, date_str: str, rx_lines: list):
    img = Image.new('RGB', (800, 1000), color='#ffffff')
    draw = ImageDraw.Draw(img)

    # Header banner
    draw.rectangle([0, 0, 800, 120], fill='#0f766e')
    draw.text((40, 25), doctor, fill='#ffffff')
    draw.text((40, 60), f"Specialty: {specialty} | Reg. No: MED-{abs(hash(doctor)) % 89999 + 10000}", fill='#ccfbf1')
    draw.text((40, 85), "Apollo Health City Hospital, Clinical Outpatient Services", fill='#ccfbf1')

    # Patient info box
    draw.rectangle([40, 140, 760, 200], outline='#cbd5e1', width=1, fill='#f8fafc')
    draw.text((55, 155), "Patient Name: Rahul Sharma    Age: 58 Yrs    Gender: Male", fill='#1e293b')
    draw.text((55, 175), f"Date of Consultation: {date_str}       Prescription ID: RX-{abs(hash(date_str)) % 9000 + 1000}", fill='#475569')

    # Rx symbol
    draw.text((45, 220), "℞", fill='#0f766e')
    draw.line([40, 260, 760, 260], fill='#0f766e', width=2)

    # Medicines
    y = 280
    for idx, line in enumerate(rx_lines, 1):
        draw.text((50, y), f"{idx}. {line['name']}", fill='#0f172a')
        y += 24
        draw.text((70, y), f"Dosage: {line['dose']}  |  Freq: {line['freq']}  |  Duration: {line['dur']}", fill='#334155')
        y += 22
        draw.text((70, y), f"Instructions: {line['inst']}", fill='#64748b')
        y += 40
        draw.line([60, y - 10, 740, y - 10], fill='#f1f5f9', width=1)

    # Footer & Doctor Signature
    draw.line([40, 880, 760, 880], fill='#e2e8f0', width=1)
    draw.text((550, 895), "Authorized Signature", fill='#475569')
    draw.line([530, 930, 720, 930], fill='#0f172a', width=1)
    draw.text((540, 940), doctor, fill='#0f766e')
    draw.text((40, 940), "Emergency Contact: 108 | MediGuard Verified Clinic", fill='#94a3b8')

    out_path = SAMPLES_DIR / filename
    img.save(out_path)
    print(f"Created sample prescription image: {out_path}")

def create_prescription_pdf(filename: str, doctor: str, specialty: str, date_str: str, rx_lines: list):
    out_path = SAMPLES_DIR / filename
    c = canvas.Canvas(str(out_path), pagesize=letter)
    width, height = letter

    # Header
    c.setFillColorRGB(0.06, 0.46, 0.43) # #0f766e
    c.rect(0, height - 100, width, 100, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 40, doctor)
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 60, f"Specialty: {specialty} | Medical Registration: DMC-84920")
    c.drawString(40, height - 75, "Department of Orthopedics & Joint Reconstruction")

    # Patient info
    c.setFillColorRGB(0.97, 0.98, 0.99)
    c.rect(40, height - 160, width - 80, 45, fill=1, stroke=1)
    c.setFillColorRGB(0.1, 0.15, 0.2)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(55, height - 135, "Patient: Rahul Sharma    Age: 58 Y / Male    Date: " + date_str)
    c.setFont("Helvetica", 8)
    c.drawString(55, height - 150, "Diagnosis: Degenerative Osteoarthritis / Joint Pain Consultation")

    # Rx symbol
    c.setFillColorRGB(0.06, 0.46, 0.43)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(40, height - 190, "Rx")

    # Medicine lines
    y = height - 220
    c.setFillColorRGB(0, 0, 0)
    for idx, item in enumerate(rx_lines, 1):
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, f"{idx}. {item['name']}")
        y -= 16
        c.setFont("Helvetica", 9)
        c.drawString(70, y, f"Dose: {item['dose']}  |  Freq: {item['freq']}  |  Duration: {item['dur']}")
        y -= 14
        c.drawString(70, y, f"Instructions: {item['inst']}")
        y -= 25

    # Disclaimer
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(40, 50, "Please follow strictly as advised. Consult before modifying medication dosages.")
    c.drawString(420, 50, "Signed: " + doctor)

    c.save()
    print(f"Created sample prescription PDF: {out_path}")

if __name__ == "__main__":
    # 1. Dr. A. Kumar
    create_prescription_image(
        "dr_kumar_rx.png",
        "Dr. A. Kumar, MD, DM (Cardiology)",
        "Interventional Cardiology",
        "15 August 2026",
        [
            {"name": "Atorvastatin 20 mg", "dose": "1 tablet", "freq": "Once daily at bedtime", "dur": "30 days", "inst": "Take after dinner"},
            {"name": "Clopidogrel 75 mg", "dose": "1 tablet", "freq": "Once daily", "dur": "30 days", "inst": "Take in the morning after breakfast"},
            {"name": "Aspirin 75 mg (Ecosprin)", "dose": "1 tablet", "freq": "Once daily", "dur": "30 days", "inst": "Take with lunch, swallow whole"}
        ]
    )

    # 2. Dr. S. Ravi
    create_prescription_image(
        "dr_ravi_rx.png",
        "Dr. S. Ravi, MBBS, MD (General Medicine)",
        "Internal Medicine",
        "20 August 2026",
        [
            {"name": "Dolo 650 (Paracetamol 650 mg)", "dose": "1 tablet", "freq": "Three times daily (1-1-1)", "dur": "5 days", "inst": "Take after meals for fever and body ache"},
            {"name": "Omeprazole 20 mg (Omez)", "dose": "1 capsule", "freq": "Once daily in morning", "dur": "14 days", "inst": "Take 30 minutes before breakfast"},
            {"name": "Amoxicillin 500 mg", "dose": "1 capsule", "freq": "Twice daily (1-0-1)", "dur": "7 days", "inst": "Complete full course, take after food"}
        ]
    )

    # 3. Dr. Priya Nair
    create_prescription_pdf(
        "dr_priya_rx.pdf",
        "Dr. Priya Nair, MS (Ortho), MCh",
        "Orthopedic Surgery & Joint Care",
        "01 September 2026",
        [
            {"name": "Ibuprofen 400 mg (Brufen)", "dose": "1 tablet", "freq": "Twice daily (1-0-1)", "dur": "10 days", "inst": "Take strictly after food with water"},
            {"name": "Paracetamol 500 mg", "dose": "2 tablets", "freq": "Twice daily (2-0-2)", "dur": "10 days", "inst": "For severe knee discomfort (Total 2000 mg/day)"},
            {"name": "Pantoprazole 40 mg (Pan 40)", "dose": "1 tablet", "freq": "Once daily", "dur": "10 days", "inst": "Morning before breakfast for gastric protection"}
        ]
    )
