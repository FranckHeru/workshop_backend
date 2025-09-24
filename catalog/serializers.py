from rest_framework import serializers
from .models import Service, Part

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = '__all__'
