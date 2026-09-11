import requests
import json
import math
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Location:
    """Lokacijos duomenys"""
    latitude: float
    longitude: float
    name: str = ""

class FuelPriceComparator:
    """Degaliniu kainu palyginimo sistema su lokacijos filtravimu"""
    
    def __init__(self):
        # Fuel.api atvirais duomenimis
        self.api_base_url = "https://api.fuel.api"
        self.fuel_types = {
            "95": "Benzinas 95",
            "98": "Benzinas 98", 
            "D": "Dyzelis",
            "LPG": "LPG"
        }
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Apskaičiuoti atstumą tarp dviejų GPS koordinačių (km)
        Haversine formulė
        """
        R = 6371  # Žemės spindulys km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def get_prices_from_api(self) -> List[Dict]:
        """Paimti degaliniu kainas iš atviraus API"""
        try:
            response = requests.get(f"{self.api_base_url}/prices/lt")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Klaida: {response.status_code}")
                return []
        except Exception as e:
            print(f"Ryšio klaida: {e}")
            return []
    
    def get_nearby_stations(
        self, 
        user_location: Location, 
        radius_km: float = 50.0
    ) -> List[Dict]:
        """
        Rasti degalines šalia vartotojo (nurodytame spindulyje)
        """
        prices = self.get_prices_from_api()
        nearby = []
        
        for station in prices:
            # Tikrinti ar yra GPS koordinatės
            if not station.get("latitude") or not station.get("longitude"):
                continue
            
            distance = self.calculate_distance(
                user_location.latitude,
                user_location.longitude,
                station.get("latitude"),
                station.get("longitude")
            )
            
            if distance <= radius_km:
                station["distance_km"] = round(distance, 2)
                nearby.append(station)
        
        return nearby
    
    def compare_prices_by_location(
        self, 
        user_location: Location,
        fuel_type: str = "95",
        radius_km: float = 50.0
    ) -> List[Dict]:
        """
        Palyginti kainas pagal kurą ir atstumą nuo vartotojo
        """
        nearby_stations = self.get_nearby_stations(user_location, radius_km)
        
        filtered = [
            {
                "degaline": s.get("station_name"),
                "vieta": s.get("location", s.get("city")),
                "kaina": s.get(f"price_{fuel_type}"),
                "atstumas_km": s.get("distance_km"),
                "latitude": s.get("latitude"),
                "longitude": s.get("longitude"),
                "data": s.get("timestamp"),
                "address": s.get("address", "")
            }
            for s in nearby_stations if s.get(f"price_{fuel_type}")
        ]
        
        # Rūšiuoti pagal kainą
        filtered.sort(key=lambda x: x["kaina"])
        return filtered
    
    def find_best_price_nearby(
        self,
        user_location: Location,
        fuel_type: str = "95",
        radius_km: float = 50.0
    ) -> Optional[Dict]:
        """
        Rasti pigiausią degalinę šalia vartotojo
        """
        nearby = self.compare_prices_by_location(user_location, fuel_type, radius_km)
        
        if nearby:
            best = nearby[0]
            return {
                "degaline": best["degaline"],
                "vieta": best["vieta"],
                "address": best["address"],
                "kaina": best["kaina"],
                "atstumas_km": best["atstumas_km"],
                "kuras": self.fuel_types.get(fuel_type),
                "sutaupymas": self.calculate_savings(nearby, fuel_type)
            }
        return None
    
    def calculate_savings(self, stations: List[Dict], fuel_type: str) -> Dict:
        """
        Apskaičiuoti santaupas (brangiausios vs pigiausios)
        """
        if len(stations) < 2:
            return {"santaupa_procentais": 0, "santaupa_eurais": 0}
        
        cheapest = stations[0]["kaina"]
        most_expensive = stations[-1]["kaina"]
        
        santaupa_eurais = round(most_expensive - cheapest, 2)
        santaupa_procentais = round((santaupa_eurais / most_expensive) * 100, 1)
        
        return {
            "santaupa_eurais": santaupa_eurais,
            "santaupa_procentais": santaupa_procentais
        }
    
    def generate_report_with_location(
        self,
        user_location: Location,
        fuel_type: str = "95",
        radius_km: float = 50.0,
        show_top_n: int = 5
    ) -> str:
        """
        Sugeneruoti ataskaitą su lokacijos duomenimis
        """
        nearby = self.compare_prices_by_location(user_location, fuel_type, radius_km)
        fuel_name = self.fuel_types.get(fuel_type, fuel_type)
        
        report = f"Degaliniu Kainu Ataskaita - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        report += "=" * 70 + "\n"
        report += f"Jūsų lokacija: {user_location.name} (Lat: {user_location.latitude}, Lon: {user_location.longitude})\n"
        report += f"Paieškos spindulys: {radius_km} km\n"
        report += f"Kuras: {fuel_name}\n"
        report += "=" * 70 + "\n\n"
        
        if not nearby:
            report += f"Nėra degalinių {radius_km} km spindulyje su {fuel_name}\n"
            return report
        
        savings = self.calculate_savings(nearby, fuel_type)
        report += f"Santaupa: €{savings['santaupa_eurais']} ({savings['santaupa_procentais']}%)\n"
        report += f"Iš viso rasta: {len(nearby)} degalinių\n\n"
        
        report += f"TOP {min(show_top_n, len(nearby))} PIGIAUSIOS:\n"
        report += "-" * 70 + "\n"
        report += f"{'#':<3} {'Degalinė':<20} {'Vieta':<15} {'Atstumas':<10} {'Kaina':<8}\n"
        report += "-" * 70 + "\n"
        
        for i, station in enumerate(nearby[:show_top_n], 1):
            report += f"{i:<3} {station['degaline'][:19]:<20} "
            report += f"{station['vieta'][:14]:<15} {station['atstumas_km']:<10} "
            report += f"€{station['kaina']}\n"
        
        return report
    
    def get_all_fuel_comparison(
        self,
        user_location: Location,
        radius_km: float = 50.0
    ) -> Dict[str, List[Dict]]:
        """
        Palyginti visų tipų kurams iš geriausios degalinės
        """
        comparison = {}
        
        for fuel_code, fuel_name in self.fuel_types.items():
            nearby = self.compare_prices_by_location(user_location, fuel_code, radius_km)
            if nearby:
                comparison[fuel_name] = nearby[:3]  # Top 3
        
        return comparison


# Pavyzdinės Lietuvos lokacijos
SAMPLE_LOCATIONS = {
    "vilnius": Location(latitude=54.6872, longitude=25.2797, name="Vilnius"),
    "kaunas": Location(latitude=54.8973, longitude=23.9021, name="Kaunas"),
    "klaipeda": Location(latitude=55.7206, longitude=21.1441, name="Klaipėda"),
    "siauliai": Location(latitude=55.9311, longitude=23.3162, name="Šiauliai"),
    "panevezys": Location(latitude=55.7386, longitude=24.3633, name="Panevėžys"),
}


# Naudojimas
if __name__ == "__main__":
    comparator = FuelPriceComparator()
    
    # Pavyzdys su Vilniaus lokacija
    vilnius = SAMPLE_LOCATIONS["vilnius"]
    
    print(comparator.generate_report_with_location(
        user_location=vilnius,
        fuel_type="D",  # Dyzelis
        radius_km=30.0,
        show_top_n=5
    ))
    
    print("\n" + "=" * 70 + "\n")
    
    # Rasti pigiausią dyzelį
    best_diesel = comparator.find_best_price_nearby(
        user_location=vilnius,
        fuel_type="D",
        radius_km=30.0
    )
    
    if best_diesel:
        print("GERIAUSIA PASIŪLYMA:")
        print(f"Degalinė: {best_diesel['degaline']}")
        print(f"Vieta: {best_diesel['vieta']}")
        print(f"Adresas: {best_diesel['address']}")
        print(f"Kaina: €{best_diesel['kaina']}")
        print(f"Atstumas: {best_diesel['atstumas_km']} km")
