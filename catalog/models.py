# catalog/models.py
from django.db import models


class Service(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    labor_minutes = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}" if self.code else self.name


class Part(models.Model):
    sku = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=150)
    unit = models.CharField(max_length=10, default="UNI")
    stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.sku} - {self.name}" if self.sku else self.name
