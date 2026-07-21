from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import StationRecommendationService, fetch_all_travel_times, recommend_top_stations
from origin.models import Origin

class StationCandidateView(APIView):
    def post(self, request):
        appointment_code = request.data.get("appointment_code")
        origins = Origin.objects.filter(appointment_code=appointment_code)
        participants_coords = [
            {"name": origin.name, "lat": float(origin.latitude), "lng": float(origin.longitude)}
            for origin in origins
        ]

        if not participants_coords:
            return Response({"error": "참여자 좌표 데이터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
      ##### 서비스 레이어 호출 #####

        #참여자들의 위경도 평균을 기준으로 후보역을 추출한다 (반경 3km 이내)
        candidates = StationRecommendationService.get_recommended_candidates(participants_coords)

        #각 후보역에 대해, 참여자들의 대중교통 이동시간을 추출한다
        travel_times = fetch_all_travel_times(candidates["candidates"], participants_coords)

        #참여자별 대중교통 이동시간의 표준편차와 평균을 사용해 1, 2, 3위 역을 추출한다
        result = recommend_top_stations(candidates["candidates"], travel_times)

        return Response(result, status=status.HTTP_200_OK)
