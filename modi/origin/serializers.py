from rest_framework import serializers
from .models import Origin


# POST 요청 body용
class OriginCreateSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    class Meta:
        model = Origin
        fields = ['name', 'origin', 'latitude', 'longitude']

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("latitude는 -90~90 범위여야 합니다.")
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("longitude는 -180~180 범위여야 합니다.")
        return value


# POST 요청의 응답 body용
class OriginResponseSerializer(serializers.ModelSerializer):
    origin_id = serializers.IntegerField(source='id')
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    class Meta:
        model = Origin
        fields = ['origin_id', 'name', 'origin', 'latitude', 'longitude']


# GET 요청의 응답 body용
class CurrentOriginsSerializer(serializers.ModelSerializer):
    origin_id = serializers.IntegerField(source='id')
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    class Meta:
        model = Origin
        fields = ['origin_id', 'name', 'origin', 'latitude', 'longitude']