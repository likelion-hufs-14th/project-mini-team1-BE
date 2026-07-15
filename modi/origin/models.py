from django.db import models

# Create your models here.
class Origin(models.Model):
    appointment_code = models.IntegerField() #appointment 모델 업데이트 후 외래키로 변경
    name = models.CharField(max_length=50)
    origin_name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.appointment_code} - {self.name} - {self.origin_name}"