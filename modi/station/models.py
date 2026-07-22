from django.db import models
from appointment.models import Appointment


class Station(models.Model):
    name = models.CharField(max_length=50)
    line = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return f"{self.name} ({self.line})"
# Create your models here.

class RecommendedStation(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="recommended_stations")
    place_num = models.IntegerField()  # 1위, 2위, 3위
    station_name = models.CharField(max_length=50)
    lines = models.JSONField()  # ["2호선", "신분당선"] 등 리스트 형태로 저장
    average_time = models.IntegerField()
    is_recommended = models.BooleanField(default=False)
    participants = models.JSONField()  # [{"name": "참여자A", "time": 17}, ...] 형태 저장
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['place_num']