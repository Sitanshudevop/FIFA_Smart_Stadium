class GoogleMapsMockClient:
    def __init__(self):
        self.stadiums = {
            "MetLife Stadium, East Rutherford, NJ": {"lat": 40.8128, "lng": -74.0745},
            "AT&T Stadium, Dallas": {"lat": 32.7473, "lng": -97.0945},
            "Mercedes-Benz Stadium, Atlanta": {"lat": 33.7554, "lng": -84.4006},
            "Hard Rock Stadium, Miami": {"lat": 25.9580, "lng": -80.2389},
            "Gillette Stadium, Boston": {"lat": 42.0909, "lng": -71.2643},
            "Lincoln Financial Field, Philadelphia": {"lat": 39.9012, "lng": -75.1675},
            "NRG Stadium, Houston": {"lat": 29.6847, "lng": -95.4107},
            "Lumen Field, Seattle": {"lat": 47.5952, "lng": -122.3316},
            "Levi's Stadium, San Francisco Bay Area": {"lat": 37.4032, "lng": -121.9698},
            "SoFi Stadium, Los Angeles": {"lat": 33.9534, "lng": -118.3387},
            "Arrowhead Stadium, Kansas City": {"lat": 39.0489, "lng": -94.4839},
            "Estadio Azteca, Mexico City": {"lat": 19.3029, "lng": -99.1505},
            "Estadio BBVA, Monterrey": {"lat": 25.6702, "lng": -100.2444},
            "Estadio Akron, Guadalajara": {"lat": 20.6817, "lng": -103.4628},
            "BC Place, Vancouver": {"lat": 49.2768, "lng": -123.1119},
            "BMO Field, Toronto": {"lat": 43.6332, "lng": -79.4186},
        }

    def geocode(self, address: str) -> list:
        """
        Simulates the official Google Maps Python Client geocode response.
        Returns a list of structured dictionaries matching the GCP JSON response format.
        """
        coords = self.stadiums.get(address, {"lat": 0.0, "lng": 0.0})
        
        return [
            {
                "address_components": [],
                "formatted_address": address,
                "geometry": {
                    "location": {
                        "lat": coords["lat"],
                        "lng": coords["lng"]
                    },
                    "location_type": "ROOFTOP",
                    "viewport": {
                        "northeast": {"lat": coords["lat"] + 0.01, "lng": coords["lng"] + 0.01},
                        "southwest": {"lat": coords["lat"] - 0.01, "lng": coords["lng"] - 0.01}
                    }
                },
                "place_id": f"mock_place_id_{hash(address)}",
                "types": ["stadium", "point_of_interest", "establishment"]
            }
        ]
