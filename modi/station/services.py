import math
from origin.models import Origin
from .models import Station


def get_centroid_by_appointment(appointment_code):
    """해당 약속의 참여자 출발지들로 중심점 계산"""
    origins = Origin.objects.filter(appointment_code=appointment_code)
    if not origins.exists():
        return None

    n = origins.count()
    avg_lat = sum(float(o.latitude) for o in origins) / n
    avg_lng = sum(float(o.longitude) for o in origins) / n
    return avg_lat, avg_lng


def haversine_distance(lat1, lng1, lat2, lng2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def find_candidate_stations(center_lat, center_lng, radius_km=3):
    candidates = []
    for station in Station.objects.all():
        dist = haversine_distance(center_lat, center_lng, float(station.latitude), float(station.longitude))
        if dist <= radius_km:
            candidates.append((station, dist))

    if not candidates:
        if radius_km < 12:
            return find_candidate_stations(center_lat, center_lng, radius_km * 2)
        all_stations = Station.objects.all()
        distances = [(s, haversine_distance(center_lat, center_lng, float(s.latitude), float(s.longitude))) for s in all_stations]
        distances.sort(key=lambda x: x[1])
        return [s for s, _ in distances[:5]]

    candidates.sort(key=lambda x: x[1])
    return [s for s, _ in candidates]