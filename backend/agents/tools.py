"""
tools.py — Micro-dispatcher tools for the Smart Stadium Orchestrator.

Provides isolated tool implementations that can be invoked natively by the GenAI SDK.
"""

import json

# Synthetic local data store of volunteers
_VOLUNTEERS = [
    {
        "id": "VOL-101",
        "name": "Maria Garcia",
        "current_zone": "Zone C",
        "languages_spoken": ["en", "es"],
        "role": "Medical",
        "is_available": True,
    },
    {
        "id": "VOL-102",
        "name": "Ahmed Ali",
        "current_zone": "Zone A",
        "languages_spoken": ["en", "ar", "fr"],
        "role": "Security",
        "is_available": True,
    },
    {
        "id": "VOL-103",
        "name": "David Chen",
        "current_zone": "Zone C",
        "languages_spoken": ["en", "zh"],
        "role": "Logistics",
        "is_available": False,
    },
    {
        "id": "VOL-104",
        "name": "Sophie Dubois",
        "current_zone": "Zone B",
        "languages_spoken": ["en", "fr", "es"],
        "role": "Medical",
        "is_available": True,
    },
    {
        "id": "VOL-105",
        "name": "Liam Smith",
        "current_zone": "Zone C",
        "languages_spoken": ["en"],
        "role": "Security",
        "is_available": True,
    }
]


def query_available_volunteers(zone: str, required_language: str, category: str) -> str:
    """
    Queries the local database for available stadium volunteers based on required criteria.

    Args:
        zone: The stadium zone where assistance is needed (e.g., 'Zone A', 'Zone C').
        required_language: ISO 639-1 language code (e.g., 'en', 'es', 'fr', 'ar').
        category: The specific role required (e.g., 'Medical', 'Security', 'Logistics').

    Returns:
        A concise JSON string containing a list of matching, available personnel.
    """
    matches = []
    
    for v in _VOLUNTEERS:
        if not v["is_available"]:
            continue
            
        # Basic exact matches or fallback if the LLM generalizes
        if (category.lower() in v["role"].lower() and 
            required_language.lower() in (lang.lower() for lang in v["languages_spoken"])):
            # Optionally check zone proximity, but for now exact match or return all that match role/lang
            matches.append(v)
            
    # Sort by zone proximity (exact match first)
    matches.sort(key=lambda x: 0 if x["current_zone"].lower() == zone.lower() else 1)
    
    return json.dumps([
        {
            "id": m["id"],
            "name": m["name"],
            "current_zone": m["current_zone"],
            "role": m["role"],
            "languages": m["languages_spoken"]
        } for m in matches
    ])
