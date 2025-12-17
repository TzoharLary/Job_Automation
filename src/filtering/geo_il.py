"""Geographic utilities for Israeli region mapping."""
from __future__ import annotations

from typing import Optional, Tuple

# Basic city/region mapping. Extend as needed.
CITY_TO_REGION = {
    "tel aviv": "מרכז",
    "tel-aviv": "מרכז",
    "tel aviv-yafo": "מרכז",
    "ramat gan": "מרכז",
    "givatayim": "מרכז",
    "bnei brak": "מרכז",
    "petah tikva": "מרכז",
    "kfar saba": "מרכז",
    "netanya": "מרכז",
    "herzliya": "מרכז",
    "hod hasharon": "מרכז",
    "rehovot": "שפלה",
    "rishon lezion": "מרכז",
    "holon": "מרכז",
    "bat yam": "מרכז",
    "jerusalem": "ירושלים",
    "modiin": "שפלה",
    "modiin-maccabim-reut": "שפלה",
    "haifa": "צפון",
    "kiryat ata": "צפון",
    "kiryat motzkin": "צפון",
    "kiryat yam": "צפון",
    "nahariya": "צפון",
    "zichron yaakov": "צפון",
    "hadera": "מרכז",
    "ashdod": "דרום",
    "ashkelon": "דרום",
    "beer sheva": "דרום",
    "beersheba": "דרום",
    "eilat": "דרום",
    "yokneam": "צפון",
    "raanana": "מרכז",
    "ra'anana": "מרכז",
    "nazareth": "צפון",
    "afula": "צפון",
    "tiberias": "צפון",
    "nahariya": "צפון",
    "metula": "צפון",
    "karmiel": "צפון",
    "sderot": "דרום",
    "ofakim": "דרום",
    "kiryat gat": "דרום",
    "kiryat malachi": "דרום",
    "ariel": "מרכז",
    "lod": "מרכז",
    "ramla": "מרכז",
    "yavne": "מרכז",
    "gaon": "מרכז",
    "shoam": "מרכז",
    "airport city": "מרכז",
    "remote": "מרכז",  # default region for remote roles if flagged Israeli context
    "israel": "מרכז",
}

REGION_DEFAULT = "אחר"


def normalize_location(raw: str | None) -> str:
    if not raw:
        return ""
    return raw.strip().lower()


def resolve_region(raw_location: str | None) -> Tuple[bool, str, Optional[str]]:
    """
    Resolve a raw location string to (is_in_israel, region, normalized_city).

    - Accepts English city names; Hebrew could be added later by extending CITY_TO_REGION
      or pre-processing with transliteration.
    - If the location is empty, returns (False, REGION_DEFAULT, None).
    - Remote roles default to region CENTER unless indicated otherwise.
    """
    loc = normalize_location(raw_location)
    if not loc:
        return False, REGION_DEFAULT, None

    if "remote" in loc:
        return True, CITY_TO_REGION.get("remote", REGION_DEFAULT), "remote"

    # direct mapping
    if loc in CITY_TO_REGION:
        return True, CITY_TO_REGION[loc], loc

    # heuristic: remove punctuation
    loc_simple = loc.replace(",", " ").replace("-", " ").strip()
    if loc_simple in CITY_TO_REGION:
        return True, CITY_TO_REGION[loc_simple], loc_simple

    # no match -> treat as not-Israel (strict)
    return False, REGION_DEFAULT, loc
