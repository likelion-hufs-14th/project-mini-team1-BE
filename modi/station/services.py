import math
from .models import Station
from django.conf import settings
import requests

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    return R * c

def get_travel_time(origin_coords: tuple, destination: tuple) -> int:
    url = "https://api.odsay.com/v1/api/searchPubTransPathT"
    params = {
        "apiKey": settings.ODSAY_API_KEY,
        "SX": origin_coords[1], "SY": origin_coords[0],
        "EX": destination[1], "EY": destination[0],
    }
    try:
        res = requests.get(url, params=params, timeout=3)
        res.raise_for_status()
        data=res.json()
        return data["result"]["path"][0]["info"]["totalTime"]
    except (requests.RequestException, KeyError, IndexError):
        return None

def fetch_all_travel_times(candidates: list, origins: list) -> dict:
    """
    candidates: [{"id": ..., "latitude": ..., "longitude": ...}, ...] 형태의 dict 리스트
    """
    results = {}
    for station in candidates:
        results[station["id"]]={}
        destination=(float(station["latitude"]), float(station["longitude"]))
        for origin in origins:
            origin_coords = (origin["lat"], origin["lng"])
            travel_time = get_travel_time(origin_coords, destination)
            results[station["name"]][origin["name"]] = travel_time
    return results

class StationRecommendationService:
    @staticmethod
    def get_recommended_candidates(participants_coords, radius_km=3.0):
        """
        매서드 활용으로 변경 
        - participants_coords: [{'lat': 37.x, 'lng': 127.x}, ...] 형태의 리스트
        """
        if not participants_coords:
            return []

        # 위경도 평균
        total_lat = sum(coord['lat'] for coord in participants_coords)
        total_lng = sum(coord['lng'] for coord in participants_coords)
        center_lat = total_lat / len(participants_coords)
        center_lng = total_lng / len(participants_coords)

        # 지하철 후보 추출
        all_stations = Station.objects.all()
        candidates = []

        for station in all_stations:
            distance = haversine(center_lat, center_lng, float(station.latitude), float(station.longitude))
            if distance <= radius_km:
                candidates.append({
                    "id": station.id,
                    "name": station.name,
                    "latitude": float(station.latitude),
                    "longitude": float(station.longitude),
                    "distance_from_center": round(distance, 2)
                })

        return {
            "center": {"lat": center_lat, "lng": center_lng},
            "candidates": candidates
        }