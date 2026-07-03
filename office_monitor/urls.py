from django.contrib import admin
from django.urls import path
from devices import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    # Member 2 er API path gulo ekhane asbe pore
]