from typing import List, Dict, Any
from models.schemas import WarningItem
from services.medicine_normalization import extract_strength_mg, parse_frequency_per_day

def detect_duplicates_and_overlaps(
    medicines: List[Dict[str, Any]], 
    prescriptions_map: Dict[str, Dict[str, Any]]
) -> List[WarningItem]:
    """
    Analyzes all identified medicines across prescriptions to find:
    1. Direct duplicate medicines (same name / active ingredient across >1 doctor)
    2. Brand name aliases sharing identical active ingredients
    3. Therapeutic class overlaps (e.g. taking multiple NSAIDs or multiple PPIs)
    """
    warnings: List[WarningItem] = []
    
    # 1. Group by active ingredient
    by_ingredient: Dict[str, List[Dict[str, Any]]] = {}
    for med in medicines:
        act = (med.get("active_ingredient") or med.get("generic_name") or med.get("original_name") or "").strip().lower()
        if act and act != "unknown":
            by_ingredient.setdefault(act, []).append(med)

    for act_key, med_group in by_ingredient.items():
        if len(med_group) > 1:
            # Check if they originate from different prescriptions or multiple entries
            rx_sources = []
            for m in med_group:
                rx_id = m.get("prescription_id")
                doc = prescriptions_map.get(rx_id, {}).get("doctor_name") or "Prescription"
                rx_sources.append(f"{doc} ({m.get('original_name')})")

            # Calculate estimated combined daily dose
            total_daily_mg = 0.0
            has_dosage_calc = False
            for m in med_group:
                str_val = extract_strength_mg(m.get("strength"))
                freq_val = parse_frequency_per_day(m.get("frequency"))
                if str_val:
                    total_daily_mg += (str_val * freq_val)
                    has_dosage_calc = True

            med_names = list({m.get("original_name") for m in med_group})
            act_display = med_group[0].get("active_ingredient") or act_key.title()
            
            is_different_brands = len(med_names) > 1
            warning_title = "Possible Duplicate Active Ingredient Detected" if is_different_brands else "Duplicate Medicine Detected"
            
            desc = (
                f"The active ingredient '{act_display}' was identified across {len(med_group)} prescribed items "
                f"({', '.join(med_names)}). "
                f"Prescription sources: {', '.join(set(rx_sources))}."
            )
            
            recommendation = (
                "Please verify the intended medication plan with your doctor or pharmacist before taking both. "
                "Taking duplicate medicines or brands with the same active ingredient can lead to unintended cumulative exposure."
            )

            warnings.append(WarningItem(
                medicine_a_id=med_group[0].get("id"),
                medicine_b_id=med_group[1].get("id") if len(med_group) > 1 else None,
                medicine_a_name=med_names[0],
                medicine_b_name=med_names[1] if len(med_names) > 1 else med_names[0],
                analysis_type="duplicate",
                severity="HIGH",
                description=desc,
                concern="Unintended dual administration of the same active drug substance.",
                recommendation=recommendation,
                source="MediGuard Duplicate Ingredient Engine",
                daily_exposure_mg=round(total_daily_mg, 1) if has_dosage_calc else None,
                prescription_sources=list(set(rx_sources))
            ))

    # 2. Therapeutic Class Overlaps (e.g. Multiple NSAIDs, Multiple PPIs, Multiple Statins)
    by_class: Dict[str, List[Dict[str, Any]]] = {}
    for med in medicines:
        tclass = med.get("therapeutic_class") or "General Medication"
        if tclass and tclass not in ["General Medication", "Unclassified"]:
            by_class.setdefault(tclass, []).append(med)

    for tclass, class_group in by_class.items():
        # Check if they have DIFFERENT active ingredients but belong to the same therapeutic class
        distinct_ingredients = {m.get("active_ingredient") for m in class_group if m.get("active_ingredient")}
        if len(distinct_ingredients) > 1 and len(class_group) > 1:
            med_names = [f"{m.get('original_name')} ({m.get('active_ingredient')})" for m in class_group]
            
            # Certain combinations like NSAID + NSAID or PPI + PPI are high-risk overlaps
            severity = "HIGH" if "NSAID" in tclass or "Anticoagulant" in tclass else "MODERATE"
            
            desc = (
                f"Potential therapeutic overlap detected: {len(class_group)} medications belong to the same class "
                f"'{tclass}': {', '.join(med_names)}."
            )
            
            recommendation = (
                "Potential therapeutic overlap detected. Please confirm the intended combination with your healthcare professional. "
                "Taking multiple medications from the same therapeutic family often multiplies side effects without additional benefit."
            )

            warnings.append(WarningItem(
                medicine_a_id=class_group[0].get("id"),
                medicine_b_id=class_group[1].get("id"),
                medicine_a_name=class_group[0].get("original_name"),
                medicine_b_name=class_group[1].get("original_name"),
                analysis_type="overlap",
                severity=severity,
                description=desc,
                concern=f"Additive pharmacological action and increased adverse reactions from multiple {tclass} agents.",
                recommendation=recommendation,
                source="MediGuard Therapeutic Classification Engine"
            ))

    return warnings
