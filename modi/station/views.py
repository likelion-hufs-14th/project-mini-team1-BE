from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import StationRecommendationService

class StationCandidateView(APIView):
    def post(self, request):
        # 프론트에서 전달받을 출발지 좌표 리스트
        # 예: {"participants": [{"lat": 37.12, "lng": 127.54}, ...]}
        participants_coords = request.data.get('participants', [])
        
        if not participants_coords:
            return Response({"error": "참여자 좌표 데이터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
        # 서비스 레이어 호출
        result = StationRecommendationService.get_recommended_candidates(participants_coords)
        
        return Response(result, status=status.HTTP_200_OK)
