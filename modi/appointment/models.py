import uuid

from django.db import models


def generate_appointment_code():
    """약속 별 랜덤 생성 코드 (예: a1b2c3)"""
    return uuid.uuid4().hex[:6]


class Appointment(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "진행중"
        COMPLETED = "COMPLETED", "완료"

    title = models.CharField(max_length=100)  # 약속 제목
    date_time = models.DateTimeField()  # 약속 날짜 및 시간 (LocalDateTime)

    appointment_code = models.CharField(  # 약속 별 랜덤 생성 코드
        max_length=12,
        unique=True,
        default=generate_appointment_code,
        editable=False,
    )

    status = models.CharField(  # 장소 추천 진행 상태
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.appointment_code})"