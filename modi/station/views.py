from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .services import StationRecommendationService
from .serializers import StationCandidateRequestSerializer, StationCandidateResponseSerializer


class StationCandidateView(APIView):

    @extend_schema(
        request=StationCandidateRequestSerializer,
        responses={200: StationCandidateResponseSerializer, 400: StationCandidateRequestSerializer},
        description='참여자들의 출발지 좌표를 받아 중간 지점 근처의 추천 지하철역 후보를 가까운 순으로 반환합니다. limit으로 최대 개수를 조절할 수 있습니다 (기본 5, 최대 20).',
    )
    def post(self, request):
        # 예: {"participants": [{"lat": 37.12, "lng": 127.54}, ...], "limit": 5}
        serializer = StationCandidateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        participants_coords = serializer.validated_data['participants']
        limit = serializer.validated_data['limit']

        result = StationRecommendationService.get_recommended_candidates(
            participants_coords, limit=limit
        )

        return Response(result, status=status.HTTP_200_OK)
