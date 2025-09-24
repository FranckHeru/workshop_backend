# core/urls.py – concentra los routers DRF (incluye quotes)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    CustomerViewSet,
    VehicleViewSet,
    ServiceViewSet,
    PartViewSet,
    WorkOrderViewSet,
)

router = DefaultRouter()
router.register(r"customers",  CustomerViewSet,  basename="customer")
router.register(r"vehicles",   VehicleViewSet,   basename="vehicle")
router.register(r"services",   ServiceViewSet,   basename="service")
router.register(r"parts",      PartViewSet,      basename="part")
router.register(r"workorders", WorkOrderViewSet, basename="workorder")
# NOTA: No registramos WorkLog porque no existe y no es necesario para los tests mínimos.

# ⬇️ Integra el router de la app quotes (cotizaciones), si está instalada
try:
    from quotes.urls import router as quotes_router  # agrega /quotations
    # Unimos los registros para mantener un único prefijo /api/
    router.registry.extend(quotes_router.registry)
except Exception:
    # Si quotes aún no está lista/no instalada, ignoramos sin romper el proyecto
    pass

urlpatterns = [
    # JWT
    path("auth/jwt/create/",  TokenObtainPairView.as_view(), name="jwt-create"),
    path("auth/jwt/refresh/", TokenRefreshView.as_view(),    name="jwt-refresh"),

    # API (todos los endpoints en un único router)
    path("", include(router.urls)),
]
