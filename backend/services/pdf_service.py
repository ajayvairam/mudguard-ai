import io
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def generate_medication_summary_pdf(analysis_data: Dict[str, Any], patient_name: str = "Patient") -> bytes:
    """
    Generates the official MediGuard AI Consolidated Medication Summary PDF matching Section 27.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f766e') # Teal-700
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1f2937')
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0f766e'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#374151')
    )
    alert_style = ParagraphStyle(
        'AlertText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#b91c1c')
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#6b7280')
    )

    story = []

    # Header
    story.append(Paragraph("MediGuard AI", title_style))
    story.append(Paragraph("Consolidated Medication Summary", subtitle_style))
    story.append(Spacer(1, 8))

    # Patient & Meta Info Table
    analysis_date = datetime.now().strftime("%d %B %Y")
    info_data = [
        [
            Paragraph(f"<b>Patient Name:</b> {patient_name}", body_style),
            Paragraph(f"<b>Date of Analysis:</b> {analysis_date}", body_style)
        ]
    ]
    info_table = Table(info_data, colWidths=[270, 260])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdfa')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#99f6e4')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    # 1. Prescription Sources
    story.append(Paragraph("1. Prescription Sources Analyzed", section_heading))
    prescriptions = analysis_data.get("prescriptions", [])
    if prescriptions:
        rx_rows = [["Prescription", "Doctor", "Date", "Items Identified"]]
        for idx, rx in enumerate(prescriptions, start=1):
            rx_rows.append([
                rx.get("file_name", f"Prescription #{idx}"),
                rx.get("doctor_name", "Physician"),
                str(rx.get("prescription_date", "N/A")),
                str(rx.get("medicines_count", 0))
            ])
        rx_table = Table(rx_rows, colWidths=[160, 160, 110, 100])
        rx_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(rx_table)
    else:
        story.append(Paragraph("No prescriptions recorded.", body_style))
    story.append(Spacer(1, 10))

    # 2. Medication Summary Table
    story.append(Paragraph("2. Consolidated Medication Summary", section_heading))
    plan_items = analysis_data.get("consolidated_plan", [])
    if plan_items:
        med_rows = [["Medicine", "Strength", "Dose", "Frequency", "Duration", "Status"]]
        for p in plan_items:
            status_color = colors.HexColor('#dc2626') if p.get("requires_review") else colors.HexColor('#16a34a')
            med_rows.append([
                Paragraph(f"<b>{p.get('medicine_name')}</b>", body_style),
                p.get("strength") or "-",
                p.get("dosage") or "1 tablet",
                p.get("frequency") or "-",
                p.get("duration") or "-",
                Paragraph(f"<font color='{status_color.hexval()}'><b>{'REVIEW REQ.' if p.get('requires_review') else 'ACTIVE'}</b></font>", body_style)
            ])
        med_table = Table(med_rows, colWidths=[140, 75, 75, 95, 75, 70])
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f766e')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(med_table)
    story.append(Spacer(1, 10))

    # 3. Medication Schedule (Morning / Afternoon / Evening / Night)
    story.append(Paragraph("3. Daily Medication Schedule", section_heading))
    sched_map = {"Morning": [], "Afternoon": [], "Evening": [], "Night": []}
    for p in plan_items:
        slots = p.get("schedule_slots", ["Morning"])
        for s in slots:
            if s in sched_map:
                sched_map[s].append(f"{p.get('medicine_name')} ({p.get('dosage') or '1 tab'} - {p.get('instructions') or 'as directed'})")
    
    sched_rows = [
        [Paragraph("<b>Time Slot</b>", body_style), Paragraph("<b>Scheduled Medicines</b>", body_style)],
        [Paragraph("<b>Morning</b> (08:00 AM)", body_style), Paragraph("<br/>".join(sched_map["Morning"]) or "None", body_style)],
        [Paragraph("<b>Afternoon</b> (01:00 PM)", body_style), Paragraph("<br/>".join(sched_map["Afternoon"]) or "None", body_style)],
        [Paragraph("<b>Evening</b> (06:00 PM)", body_style), Paragraph("<br/>".join(sched_map["Evening"]) or "None", body_style)],
        [Paragraph("<b>Night</b> (09:00 PM)", body_style), Paragraph("<br/>".join(sched_map["Night"]) or "None", body_style)],
    ]
    sched_table = Table(sched_rows, colWidths=[130, 400])
    sched_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(sched_table)
    story.append(Spacer(1, 10))

    # 4. Safety Warnings (Duplicates, Interactions, Dosage Concerns, Overlaps)
    warnings = analysis_data.get("warnings", [])
    if warnings:
        story.append(Paragraph("4. Medication Safety Findings & Alerts", section_heading))
        warn_rows = [["Type", "Severity", "Involved Medicines", "Clinical Recommendation"]]
        for w in warnings:
            sev = w.get("severity", "MODERATE")
            sev_color = "#dc2626" if sev in ["HIGH", "CRITICAL"] else "#d97706"
            warn_rows.append([
                w.get("analysis_type", "").replace("_", " ").upper(),
                Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", body_style),
                f"{w.get('medicine_a_name')} + {w.get('medicine_b_name') or ''}",
                Paragraph(f"<b>{w.get('concern') or ''}</b><br/>{w.get('recommendation')}", body_style)
            ])
        warn_table = Table(warn_rows, colWidths=[80, 60, 140, 250])
        warn_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#fee2e2')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#fca5a5')),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(warn_table)
        story.append(Spacer(1, 10))

    # Mandatory Legal & Safety Disclaimer (Section 27)
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=10, spaceAfter=8))
    disclaimer_text = (
        "<b>IMPORTANT HEALTHCARE SAFETY NOTICE:</b> "
        "This document is an AI-generated medication summary intended exclusively to support structured discussion "
        "with a qualified healthcare professional (physician or licensed pharmacist). It is <b>NOT a medical prescription</b> "
        "and does not replace professional medical diagnosis, judgment, or clinical advice. "
        "Never initiate, stop, or alter dosages without explicit guidance from your treating healthcare provider."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
