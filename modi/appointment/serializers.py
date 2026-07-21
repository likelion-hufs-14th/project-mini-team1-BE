from rest_framework import serializers
from .models import Appointment


# 약속생성 POST
class AppointmentCreateSerializer(serializers.ModelSerializer):
    dateTime = serializers.DateTimeField(source='date_time')

    class Meta:
        model = Appointment
        fields = ['title', 'dateTime']


# POST 응답 
class AppointmentCreateResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['appointment_code']


# GET 응답 
class AppointmentStatusSerializer(serializers.ModelSerializer):
    dateTime = serializers.DateTimeField(source='date_time')
    class Meta:
        model = Appointment
        fields = ['status', 'title', 'dateTime']


# 지하철역 후보 추천(이동)
class CandidateRequestSerializer(serializers.Serializer):
    limit = serializers.IntegerField(required=False, default=5, min_value=1, max_value=20)


class StationCandidateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    distance_from_center = serializers.FloatField()


class CenterPointSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()


class CandidateResponseSerializer(serializers.Serializer):
    center = CenterPointSerializer()
    candidates = StationCandidateSerializer(many=True)