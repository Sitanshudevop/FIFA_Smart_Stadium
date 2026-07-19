from typing import Any, Dict

MOCK_VOLUNTEERS = [
    {
        "id": "vol-001",
        "name": "Elena R.",
        "zone": "Zone B",
        "languages": ["en", "es"],
        "is_available": True,
    },
    {
        "id": "vol-002",
        "name": "Marcus T.",
        "zone": "Zone A",
        "languages": ["en", "de"],
        "is_available": False,
    },
    {
        "id": "vol-003",
        "name": "Aisha K.",
        "zone": "Zone B",
        "languages": ["en", "ar", "fr"],
        "is_available": True,
    },
    {
        "id": "vol-004",
        "name": "Liam J.",
        "zone": "Zone C",
        "languages": ["en"],
        "is_available": True,
    },
    {
        "id": "vol-005",
        "name": "Sofia G.",
        "zone": "Zone A",
        "languages": ["en", "pt", "es"],
        "is_available": True,
    },
]


def find_optimal_volunteer(zone: str, language: str) -> Dict[str, Any]:
    """Finds the best available volunteer based on zone and language."""
    for vol in MOCK_VOLUNTEERS:
        if vol["is_available"] and vol["zone"] == zone and language in vol["languages"]:
            return vol

    # Fallback if no exact match
    for vol in MOCK_VOLUNTEERS:
        if vol["is_available"] and vol["zone"] == zone:
            return vol

    return {"error": "No available volunteers found in the requested zone."}
