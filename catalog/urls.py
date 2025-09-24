# catalog/urls.py
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, PartViewSet

router = DefaultRouter()
router.register(r"services", ServiceViewSet, basename="service")
router.register(r"parts", PartViewSet, basename="part")

urlpatterns = router.urls
