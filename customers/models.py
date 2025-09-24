from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    address = models.CharField(max_length=255, blank=True, default="")

    def __str__(self) -> str:
        return self.name
