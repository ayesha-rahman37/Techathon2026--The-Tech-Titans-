from django.contrib import admin
from .models import Room, Device, DeviceLog, Alert

admin.site.register(Room)
admin.site.register(Device)
admin.site.register(DeviceLog)
admin.site.register(Alert)