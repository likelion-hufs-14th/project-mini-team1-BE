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

def get_travel_time(origin_coords: tuple, destination: tuple) -> int | None:
    url = "https://api.odsay.com/v1/api/searchPubTransPathT"
    params = {
        "apiKey": settings.ODSAY_API_KEY,
        "SX": origin_coords[1], "SY": origin_coords[0],
        "EX": destination[1], "EY": destination[0],
    }
    try:
        res = requests.get(url, params=params, timeout=3)
        res.raise_for_status()
        data = res.json()
        return data["result"]["path"][0]["info"]["totalTime"]
    except (requests.RequestException, KeyError, IndexError):
        return None

def fetch_all_travel_times(candidates: list, origins: list) -> dict:
    """
    candidates: [{"name": ..., "latitude": ..., "longitude": ...}, ...] 형태의 dict 리스트
    """
    results = {}
    for station in candidates:
        station_name = station["name"]
        results[station_name] = {}
        destination = (float(station["latitude"]), float(station["longitude"]))
        for origin in origins:
            origin_coords = (origin["lat"], origin["lng"])
            travel_time = get_travel_time(origin_coords, destination)
            results[station_name][origin["name"]] = travel_time
    return results

def calculate_station_stats(station_travel_times: dict) -> dict | None:
    valid_times = [t for t in station_travel_times.values() if t is not None]

    if len(valid_times) < 2:
        return None

    return {
        "stddev": statistics.stdev(valid_times),
        "mean": statistics.mean(valid_times),
        "valid_count": len(valid_times),
        "total_count": len(station_travel_times),
    }

def recommend_top_stations(candidates: list, travel_times: dict, top_n: int = 3) -> list:
    station_results = []
    for station in candidates:
        station_name = station["name"]
        station_times = travel_times.get(station_name, {})
        stats = calculate_station_stats(station_times)

        if stats is None:
            continue

        participants_info = [
            {"name": name, "time": time}
            for name, time in station_times.items()
            if time is not None
        ]

        station_results.append({
            "station": station_name,
            "lines": station["lines"],  # 이미 리스트 형태로 병합된 lines 사용
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


def get_central_point(participants_coords):

    total_lat = sum(coord['lat'] for coord in participants_coords)
    total_lng = sum(coord['lng'] for coord in participants_coords)
    center_lat = total_lat / len(participants_coords)
    center_lng = total_lng / len(participants_coords)

    result = (center_lat, center_lng)

    return result

def get_recommended_candidates(participants_coords, radius_km=3.0):
    center_coord = get_central_point(participants_coords)
    center_lat, center_lng = center_coord[0], center_coord[1]
    all_stations = Station.objects.all()
    candidates_dict = {}

    for station in all_stations:
        distance = haversine(center_lat, center_lng, float(station.latitude), float(station.longitude))

        if distance <= radius_km:
            station_name = station.name
            raw_lines= [l.strip() for l in station.line.split(",") if l.strip()]
            if station_name not in candidates_dict:
                candidates_dict[station_name] = {
                    "id": station.id,
                    "name": station_name,
                    "lines": raw_lines,
                    "latitude": float(station.latitude),
                    "longitude": float(station.longitude),
                    "distance_from_center": round(distance, 2)
                }
            else:
                # 이미 존재하는 역인 경우 lines 목록에 새 노선들 병합 (중복 제외)
                existing_lines = candidates_dict[station_name]["lines"]
                for l in raw_lines:
                    if l not in existing_lines:
                        existing_lines.append(l)

        # dict values -> list 변환
    candidates = list(candidates_dict.values())

    return {
        "center": {"lat": center_lat, "lng": center_lng},
        "candidates": candidates
    }