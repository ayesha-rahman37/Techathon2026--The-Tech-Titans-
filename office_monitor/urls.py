from django.contrib import admin
from django.urls import path, include
from devices.views import dashboard  # আপনার অ্যাপের নাম devices হলে এটি রাখুন

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('devices.urls')),  # এটি আপনার devices অ্যাপের urls.py কে যুক্ত করবে
]