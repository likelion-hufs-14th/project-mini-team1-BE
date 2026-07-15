from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import OriginSerializer
from .models import Origin
# Create your views here.

@api_view(['GET', 'POST'])
def origin_list(request, appointment_code):
    if request.method == 'GET':
        queryset = Origin.objects.filter(appointment_code=appointment_code)
        serializer = OriginSerializer(queryset, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data.copy()
        data['appointment_code'] = appointment_code
        serializer = OriginSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)