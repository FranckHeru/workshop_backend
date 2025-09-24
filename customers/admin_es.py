# customers/admin.py (ES labels sin migraciones)
from django.contrib import admin
from django import forms
from .models import Customer

class CustomerAdminForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"
        labels = {
            "name": "Nombre",
            "phone": "Teléfono",
            "email": "Correo electrónico",
            "address": "Dirección",
            "is_active": "Activo",
        }

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    form = CustomerAdminForm
    list_display = ("name", "phone", "email")
    search_fields = ("name", "phone", "email")