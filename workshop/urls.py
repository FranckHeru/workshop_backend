# workshop/urls.py – raíz del proyecto (admin, core, healthz, schema, swagger, redoc)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from .healthz import healthz  # /healthz -> JSON simple

urlpatterns = [
    path("api/v1/", include("core.api_urls")),

    # Admin
    path("admin/", admin.site.urls),

    # API principal (incluye routers de core; dentro de core.urls puedes incluir quotes)
    path("api/", include("core.urls")),

    # Healthcheck
    path("healthz", healthz),  # GET /healthz

    # OpenAPI Schema + UIs (coincide con los enlaces del menú Jazzmin)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
