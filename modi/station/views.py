from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import StationRecommendationService, fetch_all_travel_times
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
            
        # 서비스 레이어 호출
        result = StationRecommendationService.get_recommended_candidates(participants_coords)
        travel_times = fetch_all_travel_times(result["candidates"], participants_coords)
        return Response(travel_times, status=status.HTTP_200_OK)
