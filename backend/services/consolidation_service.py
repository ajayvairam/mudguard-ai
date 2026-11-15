from typing import List, Dict, Any
from models.schemas import ConsolidatedMedication, WarningItem

def determine_schedule_slots(frequency: str) -> List[str]:
    """
    Maps clinical frequencies to morning, afternoon, evening, night slots.
    """
    f = (frequency or "").lower()
    if "three" in f or "tid" in f or "1-1-1" in f:
        return ["Morning", "Afternoon", "Night"]
    if "twice" in f or "bid" in f or "1-0-1" in f:
        return ["Morning", "Night"]
    if "four" in f or "qid" in f:
        return ["Morning", "Afternoon", "Evening", "Night"]
    if "night" in f or "bedtime" in f or "0-0-1" in f:
        return ["Night"]
    if "afternoon" in f or "0-1-0" in f:
        return ["Afternoon"]
    
    # Default once daily is morning
    return ["Morning"]

def build_consolidated_medication_plan(
    medicines: List[Dict[str, Any]],
    warnings: List[WarningItem],
    prescriptions_map: Dict[str, Dict[str, Any]]
) -> List[ConsolidatedMedication]:
    """
    Builds a proposed consolidated medication review summary.
    Flags any duplicate, overlapping, or conflicting medicines with 'requires_review = True'
    and attaches review reasons and prescribing doctor sources.
    """
    # Identify which medicine names/ingredients triggered warnings
    flagged_names = set()
    flagged_reasons: Dict[str, List[str]] = {}
    
    for w in warnings:
        for name in [w.medicine_a_name, w.medicine_b_name]:
            if name:
                n_clean = name.strip().lower()
                flagged_names.add(n_clean)
                flagged_reasons.setdefault(n_clean, []).append(f"{w.severity}: {w.analysis_type.replace('_', ' ').title()} - {w.concern or w.description}")

    # Group medicines by normalized active ingredient / generic name to present a clear review view
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for m in medicines:
        key = (m.get("active_ingredient") or m.get("generic_name") or m.get("original_name") or "Medication").strip().lower()
        grouped.setdefault(key, []).append(m)

    consolidated_items: List[ConsolidatedMedication] = []

    for key, group in grouped.items():
        primary = group[0]
        med_names = list({m.get("original_name") for m in group})
        
        # Sources
        sources = []
        for m in group:
            rx_id = m.get("prescription_id")
            doc = prescriptions_map.get(rx_id, {}).get("doctor_name") or "Physician"
            sources.append(f"{doc} ({m.get('original_name')} {m.get('strength') or ''})")
        sources = list(set(sources))

        # Check if requires review
        needs_review = False
        reasons = []
        if len(group) > 1:
            needs_review = True
            reasons.append(f"Multiple prescriptions prescribe this active substance: {', '.join(med_names)}.")

        for name in med_names:
            if name.lower() in flagged_names:
                needs_review = True
                reasons.extend(flagged_reasons.get(name.lower(), []))

        status_text = "REQUIRES PROFESSIONAL VERIFICATION" if needs_review else "ACTIVE - NO MAJOR CONFLICT"
        slots = determine_schedule_slots(primary.get("frequency") or "once daily")

        consolidated_items.append(ConsolidatedMedication(
            medicine_name=" / ".join(med_names) if len(med_names) > 1 else med_names[0],
            generic_name=primary.get("generic_name") or primary.get("active_ingredient"),
            strength=primary.get("strength"),
            dosage=primary.get("dosage") or "1 tablet",
            frequency=primary.get("frequency") or "once daily",
            duration=primary.get("duration") or "As directed",
            instructions=primary.get("instructions") or "As directed by physician",
            status=status_text,
            requires_review=needs_review,
            review_reason="; ".join(set(reasons)) if reasons else None,
            source_prescriptions=sources,
            schedule_slots=slots
        ))

    return consolidated_items
