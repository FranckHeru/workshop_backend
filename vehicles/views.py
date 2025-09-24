# vehicles/views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Vehicle
from .serializers import VehicleSerializer


class VehicleViewSet(ModelViewSet):
    queryset = Vehicle.objects.select_related("owner").all().order_by("id")
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["id", "plate", "brand", "model", "year", "owner"]
    search_fields = ["plate", "brand", "model", "vin"]
    ordering_fields = ["id", "plate", "brand", "model", "year"]
    ordering = ["id"]
