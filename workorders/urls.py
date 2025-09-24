# workorders/urls.py
from rest_framework.routers import DefaultRouter
from .views import WorkOrderViewSet

router = DefaultRouter()
router.register(r"workorders", WorkOrderViewSet, basename="workorder")

urlpatterns = router.urls
