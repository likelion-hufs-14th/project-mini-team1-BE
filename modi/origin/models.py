from django.db import models
from appointment.models import Appointment

# Create your models here.

class Origin(models.Model):
    appointment_code = models.ForeignKey(
        Appointment,
        to_field="appointment_code",
        on_delete=models.CASCADE,
        related_name="origins", # appointment.origins.all()로 역참조 가능
    )
    name= models.CharField(max_length=50)
    origin = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.appointment_code} - {self.name} - {self.origin}"
    
