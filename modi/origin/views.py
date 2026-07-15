from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import OriginCreateSerializer, OriginResponseSerializer, CurrentOriginsSerializer
from .models import Origin
# Create your views here.

@api_view(['GET', 'POST'])
def origin_list(request, appointment_code):

    #수정 전
    if request.method == 'GET':
        queryset = Origin.objects.filter(appointment_code=appointment_code)
        serializer = CurrentOriginsSerializer(queryset, many=True)
        return Response(serializer.data)
    #######
    
    elif request.method == 'POST':
        serializer = OriginCreateSerializer(data=request.data)
        if serializer.is_valid():
            origin = serializer.save(appointment_code=appointment_code)
            response_serializer = OriginResponseSerializer(origin)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)