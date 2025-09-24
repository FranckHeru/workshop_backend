from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone", "address")
    search_fields = ("name", "email", "phone", "address")
    list_filter = ()  # no filtros a campos inexistentes
