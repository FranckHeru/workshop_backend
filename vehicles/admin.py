from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate','brand','model','year','owner')
    search_fields = ('plate','vin','brand','model','owner__name')
    list_filter = ('brand','year')
