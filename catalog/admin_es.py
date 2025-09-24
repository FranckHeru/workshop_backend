# catalog/admin.py (ES labels + filtro 'Activo' sin migraciones)
from django.contrib import admin
from django import forms
from .models import Service, Part

class ActiveFilter(admin.SimpleListFilter):
    title = "Activo"
    parameter_name = "activo"
    def lookups(self, request, model_admin):
        return (("1", "Sí"), ("0", "No"))
    def queryset(self, request, queryset):
        val = self.value()
        if val == "1":
            return queryset.filter(is_active=True)
        if val == "0":
            return queryset.filter(is_active=False)
        return queryset

class ServiceAdminForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = "__all__"
        labels = {
            "code": "Código",
            "name": "Servicio",
            "price": "Precio",
            "is_active": "Activo",
        }

class PartAdminForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = "__all__"
        labels = {
            "sku": "SKU",
            "name": "Nombre",
            "unit": "Unidad",
            "stock": "Existencias",
            "cost": "Costo",
            "price": "Precio",
            "is_active": "Activo",
        }

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm
    list_display = ("code", "name", "price", "is_active")
    list_filter = (ActiveFilter,)
    search_fields = ("code", "name")

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    form = PartAdminForm
    list_display = ("sku", "name", "unit", "stock", "price", "is_active")
    list_filter = (ActiveFilter,)
    search_fields = ("sku", "name")