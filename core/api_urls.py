from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
# router.register(r"tu-recurso", TuViewSet, basename="tu-recurso")

urlpatterns = [
    path("", include(router.urls)),
]
