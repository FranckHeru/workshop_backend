from django.contrib import admin
from .models import WorkOrder, WorkOrderService, WorkOrderPart

class WorkOrderServiceInline(admin.TabularInline):
    model = WorkOrderService
    extra = 1

class WorkOrderPartInline(admin.TabularInline):
    model = WorkOrderPart
    extra = 1

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ('number','status','customer','vehicle','opened_at','closed_at')
    search_fields = ('number','customer__name','vehicle__plate')
    list_filter = ('status',)
    inlines = [WorkOrderServiceInline, WorkOrderPartInline]
