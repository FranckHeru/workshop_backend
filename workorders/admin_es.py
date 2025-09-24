# workorders/admin.py (ES labels sin migraciones)
from django.contrib import admin
from django import forms
from .models import WorkOrder

class WorkOrderAdminForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = "__all__"
        labels = {
            "number": "Número",
            "customer": "Cliente",
            "vehicle": "Vehículo",
            "status": "Estado",
            "complaint": "Queja",
            "diagnosis": "Diagnóstico",
            "notes": "Notas",
            "created_at": "Creado",
            "updated_at": "Actualizado",
        }

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    form = WorkOrderAdminForm
    list_display = ("number", "status", "customer", "vehicle")
    list_filter = ("status",)
    search_fields = ("number", "customer__name", "vehicle__plate")