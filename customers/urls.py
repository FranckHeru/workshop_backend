# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CustomerViewSet,
    VehicleViewSet,
    WorkOrderViewSet,
    WorkLogViewSet,
    ServiceViewSet,
    PartViewSet,
)

router = DefaultRouter()
router.register(r"customers", CustomerViewSet, basename="customer")
router.register(r"vehicles", VehicleViewSet, basename="vehicle")
router.register(r"workorders", WorkOrderViewSet, basename="workorder")
router.register(r"worklogs", WorkLogViewSet, basename="worklog")
router.register(r"services", ServiceViewSet, basename="service")
router.register(r"parts", PartViewSet, basename="part")

urlpatterns = [
    path("", include(router.urls)),
]
