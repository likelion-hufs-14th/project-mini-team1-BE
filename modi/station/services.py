import math, requests, statistics
from .models import Station
from django.conf import settings

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
    candidates: [{"name": ..., "latitude": ..., "longitude": ...}, ...] 형태의 dict 리스트
    """
    results = {}
    for station in candidates:
        results[station["name"]]={}
        destination=(float(station["latitude"]), float(station["longitude"]))
        for origin in origins:
            origin_coords = (origin["lat"], origin["lng"])
            travel_time = get_travel_time(origin_coords, destination)
            results[station["name"]][origin["name"]] = travel_time
    return results

def calculate_station_stats(station_travel_times: dict) -> dict | None:
    """
    station_travel_times: {name: 분(또는 None), ...}
    반환: {"stddev": ..., "mean": ..., "valid_count": ..., "total_count": ...} 또는 None
    """
    valid_times = [t for t in station_travel_times.values() if t is not None]

    if len(valid_times) < 2:
        return None

    return {
        "stddev": statistics.stdev(valid_times), #표준편차. standard deviation
        "mean": statistics.mean(valid_times), #평균 이동시간 
        "valid_count": len(valid_times), #실제로 계산에 쓰인 사람 수
        "total_count": len(station_travel_times), #원래 전체 참가자 수
    }

def recommend_top_stations(candidates: list, travel_times: dict, top_n: int=3) -> list:
    # candidates - 참여자들의 중간지점으로부터 반경 3km 이내에 있는 역들 (후보가 되는 역들)
    # travel_times - 후보역 별, 각 참여자의 이동시간

    station_results =[]
    for station in candidates:
        station_name = station["name"]
        station_times = travel_times.get(station_name, {})
        stats = calculate_station_stats(station_times) #각 역별로 참여자의 이동시간 통계를 냄

        if stats in None:
            continue

        participants_info = [
            {"name": name, "time": time}
            for name, time in station_times.items()
            if time is not None
        ]

        # line 필드가 "2호선,경의중앙선,공항철도" 형태라고 가정 → 배열로 변환
        lines = [line.strip() for line in station["line"].split(", ")]

        station_results.append({
            "station": station["name"],
            "lines": lines,
            "average_time": round(stats["mean"]),
            "stddev": stats["stddev"],
            "participants": participants_info
        })

    station_results.sort(key=lambda x: (x["stddev"], x["average_time"]))

    top_stations = station_results[:top_n]
    
    recommendations = []
    for idx, station in enumerate(top_stations, start=1):
        recommendations.append({
            "place_num": idx,
            "station": station["station"],
            "lines": station["lines"],
            "average_time": station["average_time"],
            "is_recommended": (idx == 1),
            "participants": station["participants"],
        })
    
    return recommendations



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