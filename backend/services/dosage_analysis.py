from typing import List, Dict, Any
from models.schemas import WarningItem
from services.medicine_normalization import (
    extract_strength_mg, 
    parse_frequency_per_day,
    parse_units_per_dose,
    normalize_medicine_name
)

def analyze_dosage_and_conflicts(
    medicines: List[Dict[str, Any]],
    prescriptions_map: Dict[str, Dict[str, Any]]
) -> List[WarningItem]:
    """
    1. Computes total combined daily dosage per active ingredient and checks against safe limits.
    2. Detects conflicting instructions (divergent dosage, frequencies, or durations for the same medicine).
    """
    warnings: List[WarningItem] = []

    # Group by active ingredient
    by_ingredient: Dict[str, List[Dict[str, Any]]] = {}
    for med in medicines:
        act = (med.get("active_ingredient") or med.get("generic_name") or med.get("original_name") or "").strip().lower()
        if act and act != "unknown":
            by_ingredient.setdefault(act, []).append(med)

    for act_key, group in by_ingredient.items():
        act_display = group[0].get("active_ingredient") or group[0].get("generic_name") or act_key.title()
        norm = normalize_medicine_name(act_display or act_key)
        max_limit = group[0].get("max_daily_dose_mg") or norm.get("max_daily_dose_mg")
        
        # Calculate combined daily exposure
        total_daily_mg = 0.0
        dose_items = []
        valid_calcs = 0

        for m in group:
            s_mg = extract_strength_mg(m.get("strength"))
            freq = parse_frequency_per_day(m.get("frequency"))
            units = parse_units_per_dose(m.get("dosage"))
            rx_id = m.get("prescription_id")
            doc = prescriptions_map.get(rx_id, {}).get("doctor_name") or "Doctor"
            
            if s_mg is not None:
                item_daily = s_mg * units * freq
                total_daily_mg += item_daily
                valid_calcs += 1
                dose_items.append(f"{m.get('original_name')} ({s_mg:.0f} mg × {units:g} unit × {freq:g}/day = {item_daily:.0f} mg/day from {doc})")

        # 1. Check if safe daily limit is exceeded or approaching maximum threshold
        if max_limit and valid_calcs > 0:
            if total_daily_mg > max_limit:
                severity = "CRITICAL" if total_daily_mg >= (max_limit * 1.25) else "HIGH"
                desc = (
                    f"Potential excessive daily exposure detected for active ingredient '{act_display}'. "
                    f"Combined estimated exposure across prescriptions is {total_daily_mg:.0f} mg/day, "
                    f"which exceeds the standard maximum safe daily limit of {max_limit:.0f} mg/day. "
                    f"Breakdown: {'; '.join(dose_items)}."
                )
                recommendation = (
                    f"Urgent medical review required. Total daily intake of {act_display} should not exceed "
                    f"{max_limit:.0f} mg/day without specialized physician supervision due to toxicity risks. "
                    "Please verify this immediately with a qualified healthcare professional."
                )
                warnings.append(WarningItem(
                    medicine_a_id=group[0].get("id"),
                    medicine_a_name=group[0].get("original_name"),
                    analysis_type="dosage_concern",
                    severity=severity,
                    description=desc,
                    concern=f"Exceeding maximum daily dose of {act_display} can cause organ toxicity or severe adverse events.",
                    recommendation=recommendation,
                    source="FDA / Clinical Dosage Guidelines",
                    daily_exposure_mg=round(total_daily_mg, 1),
                    safe_daily_limit_mg=float(max_limit)
                ))
            elif (len(group) > 1 and total_daily_mg >= (max_limit * 0.7)) or total_daily_mg >= (max_limit * 0.9):
                # Approaching maximum limit with multiple prescriptions
                desc = (
                    f"High cumulative daily dose for '{act_display}': {total_daily_mg:.0f} mg/day "
                    f"(approaching maximum recommended daily limit of {max_limit:.0f} mg/day across multiple prescriptions: {'; '.join(dose_items)})."
                )
                warnings.append(WarningItem(
                    medicine_a_id=group[0].get("id"),
                    medicine_a_name=group[0].get("original_name"),
                    analysis_type="dosage_concern",
                    severity="MODERATE",
                    description=desc,
                    concern=f"High cumulative exposure to {act_display}.",
                    recommendation="Review total intake with your doctor to ensure dosage remains safely below maximum thresholds.",
                    source="Clinical Dosage Guidelines",
                    daily_exposure_mg=round(total_daily_mg, 1),
                    safe_daily_limit_mg=float(max_limit)
                ))

        # 2. Check for conflicting instructions across different prescriptions for the same medicine
        if len(group) > 1:
            # Check if frequencies or durations distinctly conflict
            freqs = {m.get("frequency") for m in group if m.get("frequency")}
            durations = {m.get("duration") for m in group if m.get("duration")}
            instructions = {m.get("instructions") for m in group if m.get("instructions")}
            
            conflict_reasons = []
            if len(freqs) > 1:
                conflict_reasons.append(f"divergent frequencies ({' vs '.join(freqs)})")
            if len(durations) > 1:
                conflict_reasons.append(f"conflicting treatment durations ({' vs '.join(durations)})")
            if len(instructions) > 1:
                conflict_reasons.append(f"different instructions ({' vs '.join(instructions)})")

            if conflict_reasons:
                desc = (
                    f"Conflicting directions detected for '{act_display}' across separate prescriptions: "
                    f"{'; '.join(conflict_reasons)}. "
                    f"Sources: {'; '.join(dose_items)}."
                )
                recommendation = (
                    "The prescriptions contain different instructions for this medication. "
                    "Do not attempt to choose between them on your own. "
                    "Please ask your doctor or pharmacist which instruction should be followed."
                )
                warnings.append(WarningItem(
                    medicine_a_id=group[0].get("id"),
                    medicine_b_id=group[1].get("id") if len(group) > 1 else None,
                    medicine_a_name=group[0].get("original_name"),
                    medicine_b_name=group[1].get("original_name") if len(group) > 1 else None,
                    analysis_type="conflict",
                    severity="HIGH",
                    description=desc,
                    concern="Confusion in dosing frequency or treatment duration.",
                    recommendation=recommendation,
                    source="MediGuard Prescription Comparison Engine"
                ))

    return warnings
