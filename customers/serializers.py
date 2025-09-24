# core/serializers.py
from rest_framework import serializers
from .models import Customer, Vehicle, WorkOrder, StockItem

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"

class VehicleSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta:
        model = Vehicle
        fields = "__all__"

class WorkOrderSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())

    class Meta:
        model = WorkOrder
        fields = "__all__"

class StockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockItem
        fields = "__all__"
