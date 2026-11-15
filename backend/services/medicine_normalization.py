import json
import re
from typing import Dict, Any, Optional, Tuple
from config import DATA_DIR

DRUG_DB_PATH = DATA_DIR / "drug_database.json"

_drug_cache = None

def load_drug_database() -> list:
    global _drug_cache
    if _drug_cache is None:
        try:
            with open(DRUG_DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                _drug_cache = data.get("drugs", [])
        except Exception as e:
            print(f"Error loading drug database: {e}")
            _drug_cache = []
    return _drug_cache

def normalize_medicine_name(name: str) -> Dict[str, Any]:
    """
    Normalizes any brand, trade, or generic name to its standard active ingredient,
    generic name, therapeutic class, and typical limits.
    """
    if not name:
        return {
            "generic_name": "Unknown",
            "active_ingredient": "Unknown",
            "therapeutic_class": "Unclassified",
            "max_daily_dose_mg": None
        }

    clean_query = re.sub(r'[^a-zA-Z0-9\s]', ' ', name).strip().lower()
    drugs = load_drug_database()

    # 1. Exact match on generic name
    for drug in drugs:
        gen_lower = drug["generic_name"].lower()
        if gen_lower in clean_query or clean_query in gen_lower:
            return drug

    # 2. Check active ingredient
    for drug in drugs:
        act_lower = drug["active_ingredient"].lower()
        if act_lower in clean_query or clean_query in act_lower:
            return drug

    # 3. Check synonyms / brand names
    for drug in drugs:
        for syn in drug.get("synonyms", []):
            syn_lower = syn.lower()
            # Direct or substring match
            if syn_lower in clean_query or clean_query in syn_lower:
                return drug
            # Check individual word tokens
            syn_tokens = re.findall(r'[a-zA-Z0-9]+', syn_lower)
            query_tokens = re.findall(r'[a-zA-Z0-9]+', clean_query)
            if any(t in query_tokens for t in syn_tokens if len(t) > 3):
                return drug

    # If not found, return cleaned fallback
    return {
        "generic_name": name.strip().title(),
        "active_ingredient": name.strip().title(),
        "therapeutic_class": "General Medication",
        "max_daily_dose_mg": None,
        "standard_strengths": [],
        "warnings": ""
    }

def extract_strength_mg(strength_str: Optional[str]) -> Optional[float]:
    """
    Extracts numeric strength in milligrams (mg) from text strings.
    E.g. '500 mg' -> 500.0, '1 g' -> 1000.0, '0.5 mg' -> 0.5, '20mg' -> 20.0
    """
    if not strength_str:
        return None
    
    strength_str = strength_str.lower().strip()
    
    # Check grams (g)
    g_match = re.search(r'([0-9.]+)\s*g\b', strength_str)
    if g_match:
        try:
            return float(g_match.group(1)) * 1000.0
        except ValueError:
            pass

    # Check milligrams (mg)
    mg_match = re.search(r'([0-9.]+)\s*mg\b', strength_str)
    if mg_match:
        try:
            return float(mg_match.group(1))
        except ValueError:
            pass

    # Check standalone number if unit is omitted
    num_match = re.search(r'([0-9.]+)', strength_str)
    if num_match:
        try:
            return float(num_match.group(1))
        except ValueError:
            pass

    return None

def parse_units_per_dose(dosage_str: Optional[str]) -> float:
    """
    Parses number of units per dose from string like '2 tablets', '1 capsule', '2 tabs', '1 tab'.
    Defaults to 1.0.
    """
    if not dosage_str:
        return 1.0
    s = str(dosage_str).lower().strip()
    match = re.search(r'^([0-9.]+)', s)
    if match:
        try:
            val = float(match.group(1))
            return val if val > 0 else 1.0
        except ValueError:
            pass
    return 1.0

def parse_frequency_per_day(freq_str: Optional[str]) -> float:
    """
    Converts frequency descriptions like 'once daily', 'twice daily', '1-0-1', 'every 8 hours'
    into an estimated numeric frequency per day.
    """
    if not freq_str:
        return 1.0
        
    s = freq_str.lower().strip()
    
    # Common medical digit notation: 1-0-1 (2/day), 1-1-1 (3/day), 1-0-0 (1/day), 1-1-1-1 (4/day)
    digit_pattern = re.match(r'^([0-9])\s*[-–/]\s*([0-9])\s*[-–/]\s*([0-9])(?:\s*[-–/]\s*([0-9]))?$', s)
    if digit_pattern:
        parts = [int(p) for p in digit_pattern.groups() if p is not None]
        return float(sum(parts)) if sum(parts) > 0 else 1.0

    if "four" in s or "4 times" in s or "qid" in s or "qds" in s:
        return 4.0
    if "three" in s or "3 times" in s or "tid" in s or "tds" in s:
        return 3.0
    if "twice" in s or "2 times" in s or "bid" in s or "bds" in s:
        return 2.0
    if "once" in s or "1 time" in s or "od" in s or "daily" in s or "bedtime" in s or "morning" in s:
        return 1.0
    if "every 4 hours" in s or "q4h" in s:
        return 6.0
    if "every 6 hours" in s or "q6h" in s:
        return 4.0
    if "every 8 hours" in s or "q8h" in s:
        return 3.0
    if "every 12 hours" in s or "q12h" in s:
        return 2.0
    if "alternate" in s or "every other day" in s:
        return 0.5
    if "weekly" in s:
        return 1.0 / 7.0

    return 1.0
