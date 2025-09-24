from django.db import models
from customers.models import Customer

class Vehicle(models.Model):
    owner = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='vehicles')
    plate = models.CharField(max_length=20, unique=True)
    vin = models.CharField(max_length=50, blank=True, null=True)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=30, blank=True, null=True)
    mileage_km = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehicle'
        indexes = [
            models.Index(fields=['plate']),
            models.Index(fields=['vin']),
        ]

    def __str__(self):
        return f"{self.plate} - {self.brand} {self.model} {self.year}"
