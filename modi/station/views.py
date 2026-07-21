from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import get_recommended_candidates, fetch_all_travel_times, recommend_top_stations
from origin.models import Origin, Appointment
from .models import RecommendedStation

class StationCandidateView(APIView):
    def get(self, request, appointment_code):
        try:
            appointment = Appointment.objects.get(appointment_code=appointment_code)
        except Appointment.DoesNotExist:
            return Response({"error": "존재하지 않는 약속 코드입니다"}, status=status.HTTP_404_NOT_FOUND)
        
        saved_recommendations = RecommendedStation.objects.filter(appointment=appointment)

        if not saved_recommendations.exists():
            return Response({"error": "추천 결과가 아직 생성되지 않았습니다"}, status=status.HTTP_404_NOT_FOUND)

        result = [
            {
                "place_num": item.place_num,
                "station": item.station_name,
                "lines": item.lines,
                "average_time": item.average_time,
                "is_recommended": item.is_recommended,
                "participants": item.participants,
            }
            for item in saved_recommendations
        ]

        return Response(result, status=status.HTTP_200_OK)

    def post(self, request, appointment_code):
        try:
            appointment = Appointment.objects.get(appointment_code=appointment_code)
        except Appointment.DoesNotExist:
            return Response({"error": "존재하지 않는 약속 코드입니다"}, status=status.HTTP_404_NOT_FOUND)
        
        origins = Origin.objects.filter(appointment_code=appointment_code)
        participants_coords = [
            {"name": origin.name, "lat": float(origin.latitude), "lng": float(origin.longitude)}
            for origin in origins
        ]

        if not participants_coords:
            return Response({"error": "참여자 좌표 데이터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
      ##### 서비스 레이어 호출 #####

        #참여자들의 위경도 평균을 기준으로 후보역을 추출한다 (반경 3km 이내)
        candidates = get_recommended_candidates(participants_coords)

        #각 후보역에 대해, 참여자들의 대중교통 이동시간을 추출한다
        travel_times = fetch_all_travel_times(candidates["candidates"], participants_coords)

        #참여자별 대중교통 이동시간의 표준편차와 평균을 사용해 1, 2, 3위 역을 추출한다
        result = recommend_top_stations(candidates["candidates"], travel_times)

        RecommendedStation.objects.filter(appointment=appointment).delete()

        for item in result:
            RecommendedStation.objects.create(
                appointment=appointment,
                place_num=item["place_num"],
                station_name=item["station"],
                lines=item["lines"],
                average_time=item["average_time"],
                is_recommended=item["is_recommended"],
                participants=item["participants"],
            )

        return Response(result, status=status.HTTP_200_OK)
