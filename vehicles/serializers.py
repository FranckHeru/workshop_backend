# vehicles/serializers.py
from rest_framework import serializers
from .models import Vehicle

class VehicleSerializer(serializers.ModelSerializer):
    # El test envía owner como entero
    owner = serializers.IntegerField(write_only=True)
    owner_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Vehicle
        fields = ["id", "plate", "brand", "model", "year", "vin", "owner", "owner_info"]

    def get_owner_info(self, obj):
        if obj.owner_id and obj.owner:
            return {"id": obj.owner_id, "name": getattr(obj.owner, "name", None)}
        return None

    def create(self, validated_data):
        owner_id = validated_data.pop("owner")
        # asignamos via *_id para evitar otra query
        vehicle = Vehicle(**validated_data)
        vehicle.owner_id = owner_id
        vehicle.save()
        return vehicle

    def update(self, instance, validated_data):
        if "owner" in validated_data:
            instance.owner_id = validated_data.pop("owner")
        return super().update(instance, validated_data)
