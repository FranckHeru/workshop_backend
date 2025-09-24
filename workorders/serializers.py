from rest_framework import serializers
from workorders.models import WorkOrder
from customers.models import Customer
from vehicles.models import Vehicle


class WorkOrderSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    vehicle  = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())

    class Meta:
        model = WorkOrder
        fields = [
            "id",
            "number",
            "status",
            "complaint",
            "diagnosis",
            "notes",
            "opened_at",
            "closed_at",
            "customer",
            "vehicle",
        ]
