# workorders/views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import WorkOrder
from .serializers import WorkOrderSerializer


class WorkOrderViewSet(ModelViewSet):
    queryset = WorkOrder.objects.select_related("vehicle").all().order_by("id")
    serializer_class = WorkOrderSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["id", "status", "vehicle"]
    search_fields = ["description", "status"]
    ordering_fields = ["id", "created_at", "status"]
    ordering = ["id"]
