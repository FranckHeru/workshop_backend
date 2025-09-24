# vehicles/admin.py (ES labels sin migraciones)
from django.contrib import admin
from django import forms
from .models import Vehicle

class VehicleAdminForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = "__all__"
        labels = {
            "owner": "Propietario",
            "plate": "Placa",
            "vin": "VIN",
            "brand": "Marca",
            "model": "Modelo",
            "year": "Año",
            "color": "Color",
            "mileage_km": "Kilometraje (km)",
            "is_active": "Activo",
        }

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    form = VehicleAdminForm
    list_display = ("plate", "brand", "model", "year", "owner")
    list_filter = ("year",)
    search_fields = ("plate", "brand", "model", "vin")