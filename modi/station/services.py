import math
from django.db.models import Avg

from .models import Station
from origin.models import Origin

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R * c

class StationRecommendationService:
    @staticmethod
    def get_recommended_candidates(participants_coords, radius_km=3.0, limit=5):
       #출발지 중간 지점 -> AVG로 한번에 계산 
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

        result = Origin.objects.filter(appointment_code=appointment_code).aggregate(
            center_lat=Avg('latitude'),
            center_lng=Avg('longitude'),
        )
        if result['center_lat'] is None:
            return None
        return {
            "lat": float(result['center_lat']),
            "lng": float(result['center_lng']),
        } 
    
    @staticmethod
    def get_station_candidates(center_lat, center_lng, radius_km = 3.0, limit =5):
        lat_delta = radius_km / 111.0
        lng_delta = radius_km / (111.0 * max(math.cos(math.radians(center_lat)), 0.01))
        nearby_stations = Station.objects.filter(
            latitude__range=(center_lat - lat_delta, center_lat + lat_delta),
            longitude__range=(center_lng - lng_delta, center_lng + lng_delta),
        )

        candidates = []
        for station in nearby_stations:
            distance = haversine(center_lat, center_lng, float(station.latitude), float(station.longitude))
            if distance <= radius_km:  # bounding box는 사각형이라 모서리 오차 보정용 재확인
                candidates.append({
                    "id": station.id,
                    "name": station.name,
                    "latitude": float(station.latitude),
                    "longitude": float(station.longitude),
                    "distance_from_center": round(distance, 2),
                })

        candidates.sort(key=lambda c: c["distance_from_center"])
        return candidates[:limit]
        