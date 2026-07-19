"""
stadium_state.py — Hardcoded baseline system state for simulation.

Provides static tournament operational baselines for the crisis simulation engine,
satisfying zero-disk / memory footprint constraints.
"""

from typing import Any

STADIUM_STATE: dict[str, Any] = {
    "capacity_limits": {
        "North Stand": 25000,
        "South Stand": 25000,
        "East Tunnel": 12000,
        "West Block": 18000,
        "VIP Sector": 5000,
    },
    "volunteer_counts": {
        "medical_responders": 120,
        "security_personnel": 350,
        "guest_services": 200,
        "traffic_control": 85,
    },
    "current_weather": {
        "condition": "Clear",
        "temperature_celsius": 24,
        "wind_speed_kmh": 12,
    },
    "transit_throughput_metrics": {
        "Metro Line 1": "15,000 passengers/hour",
        "Metro Line 2": "12,000 passengers/hour",
        "Bus Terminal A": "5,000 passengers/hour",
        "Ride Share Hub": "3,000 vehicles/hour",
    },
}
