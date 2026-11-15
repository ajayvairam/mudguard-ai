import json
from typing import List, Dict, Any, Tuple, Optional
from config import DATA_DIR
from models.schemas import WarningItem

INTERACTIONS_FILE = DATA_DIR / "drug_interactions.json"

_interactions_cache = None

def load_interactions_database() -> List[Dict[str, Any]]:
    global _interactions_cache
    if _interactions_cache is None:
        try:
            with open(INTERACTIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                _interactions_cache = data.get("interactions", [])
        except Exception as e:
            print(f"Error reading interactions database: {e}")
            _interactions_cache = []
    return _interactions_cache

def check_pairwise_interaction(drug_a_name: str, drug_b_name: str) -> Optional[Dict[str, Any]]:
    """
    Checks if there is a verified clinical interaction between two drug names or active ingredients.
    Matches bidirectionally.
    """
    interactions = load_interactions_database()
    a_lower = drug_a_name.lower().strip()
    b_lower = drug_b_name.lower().strip()

    for item in interactions:
        item_a = item["drug_a"].lower().strip()
        item_b = item["drug_b"].lower().strip()

        match_forward = (item_a in a_lower or a_lower in item_a) and (item_b in b_lower or b_lower in item_b)
        match_reverse = (item_b in a_lower or a_lower in item_b) and (item_a in b_lower or b_lower in item_a)

        if match_forward or match_reverse:
            return item

    return None

def analyze_all_drug_interactions(medicines: List[Dict[str, Any]]) -> List[WarningItem]:
    """
    Evaluates all unique pairwise combinations of identified medicines against the trusted clinical database.
    """
    warnings: List[WarningItem] = []
    n = len(medicines)
    if n < 2:
        return warnings

    seen_pairs = set()

    for i in range(n):
        for j in range(i + 1, n):
            med_a = medicines[i]
            med_b = medicines[j]

            name_a = med_a.get("active_ingredient") or med_a.get("generic_name") or med_a.get("original_name")
            name_b = med_b.get("active_ingredient") or med_b.get("generic_name") or med_b.get("original_name")

            if not name_a or not name_b:
                continue

            pair_key = tuple(sorted([name_a.lower(), name_b.lower()]))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            # Check trusted interaction database
            interaction = check_pairwise_interaction(name_a, name_b)
            if not interaction:
                # Also check original brand names in case synonym matches
                brand_a = med_a.get("original_name", "")
                brand_b = med_b.get("original_name", "")
                interaction = check_pairwise_interaction(brand_a, brand_b)

            if interaction:
                warnings.append(WarningItem(
                    medicine_a_id=med_a.get("id"),
                    medicine_b_id=med_b.get("id"),
                    medicine_a_name=med_a.get("original_name", name_a),
                    medicine_b_name=med_b.get("original_name", name_b),
                    analysis_type="interaction",
                    severity=interaction.get("severity", "MODERATE"),
                    description=interaction.get("description", "A potential drug interaction was detected between these medications."),
                    concern=interaction.get("concern", "Potential clinical interaction risk."),
                    recommendation=interaction.get("action", "Please consult your prescribing physician or pharmacist before combining these medications."),
                    source=interaction.get("source", "Clinical Drug Interaction Knowledgebase")
                ))

    return warnings
