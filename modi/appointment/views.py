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


# POST /appointments  — 약속 생성
@api_view(['POST'])
def appointment_create(request):
    serializer = AppointmentCreateSerializer(data=request.data)
    if serializer.is_valid():
        appointment = serializer.save()
        response_serializer = AppointmentCreateResponseSerializer(appointment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET /appointments/<appointment_code>/status  — 약속 상태 확인
@api_view(['GET'])
def appointment_status(request, appointment_code):
    appointment = get_object_or_404(Appointment, appointment_code=appointment_code)
    serializer = AppointmentStatusSerializer(appointment)
    return Response(serializer.data, status=status.HTTP_200_OK)