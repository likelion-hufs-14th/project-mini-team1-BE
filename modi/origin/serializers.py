from rest_framework import serializers
from .models import Origin

class OriginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Origin
        fields = ['appointment_code', 'name', 'origin', 'latitude', 'longitude', 'created_at']
        read_only_fields = ['created_at']