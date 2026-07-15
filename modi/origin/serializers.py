from rest_framework import serializers
from .models import Origin, Participant

#POST 요청 body용
class OriginCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Origin
        fields = ['name', 'origin', 'latitude', 'longitude']

#POST 응답 body용
class OriginResponseSerializer(serializers.ModelSerializer):
    origin_id = serializers.IntegerField(source='id')

    class Meta:
        model = Origin
        fields = ['origin_id', 'name', 'origin']

#GET 응답 body용

class CurrentOriginsSerializer(serializers.ModelSerializer):
    origin = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = ['name', 'origin']
    
    def get_origin(self, obj):
        if hasattr(obj, 'origin'):
            return obj.origin.origin
        return None
