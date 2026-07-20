from rest_framework import serializers


class ParticipantCoordSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lng = serializers.FloatField(min_value=-180, max_value=180)


class StationCandidateRequestSerializer(serializers.Serializer):
    participants = ParticipantCoordSerializer(many=True)
    limit = serializers.IntegerField(required=False, default=5, min_value=1, max_value=20)

    def validate_participants(self, value):
        if not value:
            raise serializers.ValidationError("참여자 좌표 데이터가 없습니다.")
        return value


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