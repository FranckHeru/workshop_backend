
from django.contrib import admin
from .models import Quotation, QuotationService, QuotationPart

class QuotationServiceInline(admin.TabularInline):
    model = QuotationService
    extra = 1

class QuotationPartInline(admin.TabularInline):
    model = QuotationPart
    extra = 1

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("number", "status", "customer", "vehicle", "grand_total", "valid_until", "created_at")
    search_fields = ("number", "customer__name", "vehicle__plate", "vehicle__vin")
    list_filter = ("status", "valid_until", "created_at")
    inlines = [QuotationServiceInline, QuotationPartInline]
