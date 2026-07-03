from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, DeviceViewSet, AlertViewSet
from .views import RoomViewSet, DeviceViewSet, AlertViewSet, DeviceLogViewSet, dashboard

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'logs', DeviceLogViewSet, basename='log')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', dashboard, name='dashboard'),  
]