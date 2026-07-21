from rest_framework import serializers


class StationCandidateRequestSerializer(serializers.Serializer):
   limit = serializers.IntegerField(required=False, default =5, min_value = 1, max_value = 20)


class StationCandidateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    distance_from_center = serializers.FloatField()


class CenterPointSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()


class StationCandidateResponseSerializer(serializers.Serializer):
    center = CenterPointSerializer()
    candidates = StationCandidateSerializer(many=True)