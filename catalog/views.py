# catalog/views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Service, Part
from .serializers import ServiceSerializer, PartSerializer


class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all().order_by("id")
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["id", "name"]
    search_fields = ["name", "description"]
    ordering_fields = ["id", "name", "price"]
    ordering = ["id"]


class PartViewSet(ModelViewSet):
    queryset = Part.objects.all().order_by("id")
    serializer_class = PartSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["id", "name", "sku"]
    search_fields = ["name", "sku", "description"]
    ordering_fields = ["id", "name", "price", "stock"]
    ordering = ["id"]
