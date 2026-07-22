from rest_framework import serializers
from .models import Origin

#POST 요청 body용
class OriginCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Origin
        fields = ['appointment', 'name', 'origin', 'latitude', 'longitude']

#POST 요청의 응답 body용
class OriginResponseSerializer(serializers.ModelSerializer):
    origin_id = serializers.IntegerField(source='id')

    class Meta:
        model = Origin
        fields = ['origin_id', 'name', 'origin']

#GET 요청의 응답 body용
class CurrentOriginsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Origin
        fields = ['name', 'origin']