from django.contrib import admin
from django.urls import path, include
from devices import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('api/', include('devices.urls')),
]