# Hardcoded dictionary for zero-bloat state lookup

STADIUM_STATE = {
    "zones": {
        "Zone A": {"capacity_max": 20000, "current_occupancy": 18500, "status": "NOMINAL"},
        "Zone B": {"capacity_max": 15000, "current_occupancy": 14900, "status": "CONGESTED"},
        "Zone C": {"capacity_max": 25000, "current_occupancy": 10000, "status": "NOMINAL"}
    },
    "medical_tents": {
        "North_Tent": {"active_staff": 5, "beds_available": 2},
        "South_Tent": {"active_staff": 8, "beds_available": 10}
    },
    "transit_lines": {
        "Metro_Red": {"status": "DELAYED", "wait_time_mins": 15},
        "Bus_Shuttle_1": {"status": "OPERATIONAL", "wait_time_mins": 5}
    }
}
