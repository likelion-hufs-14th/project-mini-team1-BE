from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Appointment
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentCreateResponseSerializer,
    AppointmentStatusSerializer,
)


@extend_schema(
    request=AppointmentCreateSerializer,
    responses={
        201: AppointmentCreateResponseSerializer,
        400: OpenApiTypes.OBJECT,
    },
    description='새로운 약속을 생성합니다.',
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
    responses=AppointmentStatusSerializer,
    parameters=[
        OpenApiParameter(
            name='appointment_code',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='약속 코드',
        ),
    ],
    description='약속의 진행 상태를 조회합니다.',
)
@api_view(['GET'])
def appointment_status(request, appointment_code):
    appointment = get_object_or_404(Appointment, appointment_code=appointment_code)
    serializer = AppointmentStatusSerializer(appointment)
    return Response(serializer.data, status=status.HTTP_200_OK)