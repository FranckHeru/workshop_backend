# catalog/admin.py
from django.contrib import admin
from .models import Service, Part


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    # Campos reales del modelo Service: code, name, description, labor_minutes, price, is_active
    list_display = ("code", "name", "labor_minutes", "price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name", "description")
    ordering = ("name",)


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    # Campos reales del modelo Part: sku, name, unit, stock, cost, price, is_active
    list_display = ("sku", "name", "unit", "price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("sku", "name")
    ordering = ("name",)
