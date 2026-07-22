from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import OriginCreateSerializer, OriginResponseSerializer, CurrentOriginsSerializer
from .models import Origin, Appointment
from django.shortcuts import get_object_or_404

# Create your views here.

@api_view(['GET', 'POST'])
def origin_list(request, appointment_code):

    if request.method == 'GET':
        appointment = get_object_or_404(Appointment, appointment_code=appointment_code)
        origins = Origin.objects.filter(appointment=appointment)
        serializer = CurrentOriginsSerializer(origins, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        appointment = get_object_or_404(Appointment, appointment_code=appointment_code)
        serializer = OriginCreateSerializer(data=request.data)
        if serializer.is_valid():
            origin = serializer.save(appointment=appointment)
            response_serializer = OriginResponseSerializer(origin)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)