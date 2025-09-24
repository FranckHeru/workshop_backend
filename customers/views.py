# core/views.py
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated

from core.models import Customer, Vehicle, WorkLog
from workorders.models import WorkOrder
from catalog.models import Service, Part

from .serializers import (
    CustomerSerializer,
    VehicleSerializer,
    WorkOrderSerializer,
    WorkLogSerializer,
    ServiceSerializer,
    PartSerializer,
)


class IsAsesorCanCreate(permissions.BasePermission):
    """
    Permite crear a Asesor (y Admin). Mécanico sólo lectura.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # POST/PUT/PATCH/DELETE
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        groups = set(request.user.groups.values_list("name", flat=True))
        if "Admin" in groups or "Asesor" in groups:
            return True
        return False


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by("id")
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated & IsAsesorCanCreate]


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all().order_by("id")
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated & IsAsesorCanCreate]


class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all().order_by("-id")
    serializer_class = WorkOrderSerializer
    permission_classes = [IsAuthenticated & IsAsesorCanCreate]


class WorkLogViewSet(viewsets.ModelViewSet):
    queryset = WorkLog.objects.all().order_by("-id")
    serializer_class = WorkLogSerializer
    permission_classes = [IsAuthenticated]


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by("id")
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated & IsAsesorCanCreate]


class PartViewSet(viewsets.ModelViewSet):
    queryset = Part.objects.all().order_by("id")
    serializer_class = PartSerializer
    permission_classes = [IsAuthenticated & IsAsesorCanCreate]
