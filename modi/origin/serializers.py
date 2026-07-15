from rest_framework import serializers
from .models import Origin, Participant

#POST 요청 body용
class OriginCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    origin = serializers.CharField(max_length=200)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)

    def create(self, validated_data):
        appointment_code = self.context['appointment_code']
        participant = Participant.objects.create(
            appointment_code=appointment_code,
            name=validated_data['name']
        )
        return Origin.objects.create(
            participant=participant,
            origin=validated_data['origin'],
            latitude=validated_data['latitude'],
            longitude=validated_data['longitude']
        )

#POST 요청의 응답 body용
class OriginResponseSerializer(serializers.ModelSerializer):
    origin_id = serializers.IntegerField(source='id')
    name = serializers.CharField(source='participant.name')  # source 추가

    class Meta:
        model = Origin
        fields = ['origin_id', 'name', 'origin']

#GET 요청의 응답 body용
class CurrentOriginsSerializer(serializers.ModelSerializer):
    origin = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = ['name', 'origin']

    def get_origin(self, obj):
        if hasattr(obj, 'origin'):
            return obj.origin.origin
        return None