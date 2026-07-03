from django.urls import path, include
from rest_framework.routers import DefaultRouter  # type: ignore[reportMissingImports]
from .views import RoomViewSet, DeviceViewSet, AlertViewSet

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'alerts', AlertViewSet, basename='alert')

urlpatterns = [
    path('', include(router.urls)),
]