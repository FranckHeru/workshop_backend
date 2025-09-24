# core/serializers.py
from rest_framework import serializers

from customers.models import Customer
from vehicles.models import Vehicle
from catalog.models import Service, Part
from workorders.models import WorkOrder


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class VehicleSerializer(serializers.ModelSerializer):
    # owner -> FK a customers.Customer
    owner = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta:
        model = Vehicle
        fields = "__all__"


class ServiceSerializer(serializers.ModelSerializer):
    # Tus migraciones añaden `code` a Service, por eso fields="__all__" es correcto.
    class Meta:
        model = Service
        fields = "__all__"


class PartSerializer(serializers.ModelSerializer):
    # Tus migraciones añaden `sku` a Part (y otros campos). "__all__" lo incluye.
    class Meta:
        model = Part
        fields = "__all__"


class WorkOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrder
        fields = "__all__"
