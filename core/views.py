# core/views.py
from rest_framework import viewsets, permissions

from .serializers import (
    CustomerSerializer,
    VehicleSerializer,
    ServiceSerializer,
    PartSerializer,
    WorkOrderSerializer,
)

from customers.models import Customer
from vehicles.models import Vehicle
from catalog.models import Service, Part
from workorders.models import WorkOrder


class IsAsesorOrAdminForUnsafe(permissions.BasePermission):
    """
    GET/HEAD/OPTIONS: requiere autenticación.
    POST/PUT/PATCH/DELETE: solo Admin o Asesor.
    (Los tests piden que Mecanico no pueda crear/borrar, pero sí listar.)
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_superuser
            or request.user.groups.filter(name__in=["Admin", "Asesor"]).exists()
        )


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by("id")
    serializer_class = CustomerSerializer
    permission_classes = [IsAsesorOrAdminForUnsafe]


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all().order_by("id")
    serializer_class = VehicleSerializer
    permission_classes = [IsAsesorOrAdminForUnsafe]


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by("id")
    serializer_class = ServiceSerializer
    permission_classes = [IsAsesorOrAdminForUnsafe]


class PartViewSet(viewsets.ModelViewSet):
    queryset = Part.objects.all().order_by("id")
    serializer_class = PartSerializer
    permission_classes = [IsAsesorOrAdminForUnsafe]


class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all().order_by("id")
    serializer_class = WorkOrderSerializer
    permission_classes = [IsAsesorOrAdminForUnsafe]
