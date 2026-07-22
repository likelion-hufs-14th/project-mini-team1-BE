from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Origin
from .serializers import OriginCreateSerializer, OriginResponseSerializer, CurrentOriginsSerializer


@extend_schema_view(
    get=extend_schema(
        responses=CurrentOriginsSerializer(many=True),
        parameters=[
            OpenApiParameter(
                name='appointment_code',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='약속 코드',
            ),
        ],
        description='특정 약속에 등록된 출발지 목록을 조회합니다.',
    ),
    post=extend_schema(
        request=OriginCreateSerializer,
        responses={
            201: OriginResponseSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        description='특정 약속에 출발지를 등록합니다.',
    ),
)
@api_view(['GET', 'POST'])
def origin_list(request, appointment_code):
    if request.method == 'GET':
        origins = Origin.objects.filter(appointment_code=appointment_code)
        serializer = CurrentOriginsSerializer(origins, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = OriginCreateSerializer(data=request.data)
        if serializer.is_valid():
            origin = serializer.save(appointment_code=appointment_code)
            response_serializer = OriginResponseSerializer(origin)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)