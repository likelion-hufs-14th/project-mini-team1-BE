from django.db import models

# Create your models here.
class Participant(models.Model):
    appointment_code = models.CharField(max_length=5)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.appointment_code} - {self.name}"

class Origin(models.Model):
    participant = models.OneToOneField(
        Participant,
        on_delete=models.CASCADE,
        related_name='origin'
    )
    origin = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.appointment_code} - {self.name} - {self.origin_name}"
    
