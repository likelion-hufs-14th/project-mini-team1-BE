from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiTypes

from .models import Appointment
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentCreateResponseSerializer,
    AppointmentStatusSerializer,
    CandidateRequestSerializer,
    CandidateResponseSerializer
)

from station.services import StationRecommendationService

@extend_schema(
    methods=['POST'],
    request=AppointmentCreateSerializer,
    responses={201: AppointmentCreateResponseSerializer, 400: OpenApiTypes.OBJECT},
    description='새로운 약속을 생성하고 약속 코드를 발급합니다.',
)

@api_view(['POST'])
def appointment_create(request):
    serializer = AppointmentCreateSerializer(data=request.data)
    if serializer.is_valid():
        appointment = serializer.save()
        response_serializer = AppointmentCreateResponseSerializer(appointment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    methods=['GET'],
    responses={200: AppointmentStatusSerializer, 404: OpenApiTypes.OBJECT},
    description='약속 코드로 약속 상태를 조회합니다.',
)

@api_view(['GET'])
def appointment_status(request, appointment_code):
    appointment = get_object_or_404(Appointment, appointment_code=appointment_code)
    serializer = AppointmentStatusSerializer(appointment)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema
    methods=['POST'],
    request=CandidateRequestSerializer,
    responses={200: CandidateResponseSerializer, 400: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT},
    description='해당 약속에 등록된 출발지들의 중간 지점 근처 추천 지하철역을 가까운 순으로 반환합니다.',
)
@api_view(['POST'])
def appointment_candidates(request, appointment_code):
    get_object_or_404(Appointment, appointment_code=appointment_code)

    req_serializer = CandidateRequestSerializer(data=request.data)
    if not req_serializer.is_valid():
        return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    limit = req_serializer.validated_data['limit']

    center = StationRecommendationService.get_center_point(appointment_code)
    if center is None:
        return Response({"detail": "등록된 출발지가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

    candidates = StationRecommendationService.get_station_candidates(
        center['lat'], center['lng'], limit=limit
    )

    response_serializer = CandidateResponseSerializer({"center": center, "candidates": candidates})
    return Response(response_serializer.data, status=status.HTTP_200_OK)