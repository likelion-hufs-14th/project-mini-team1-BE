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
    class Meta:
        model = Appointment
        fields = ['status']