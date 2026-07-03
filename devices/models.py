from django.db import models
from django.utils import timezone

class Room(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Device(models.Model):
    FAN = 'fan'
    LIGHT = 'light'
    DEVICE_TYPES = [
        (FAN, 'Fan'),
        (LIGHT, 'Light')
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='devices')
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES)
    name = models.CharField(max_length=50)            
    power_watt = models.PositiveIntegerField()       
    status = models.BooleanField(default=False)       
    last_changed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.room.name} - {self.name}"

    def set_status(self, new_status: bool):
        if new_status != self.status:
            self.status = new_status
            self.last_changed = timezone.now()
            self.save()
            
            # DeviceLog মডেল নিচে থাকায় স্ট্রিং বা গ্লোবাল রেফারেন্স হিসেবে কল করা নিরাপদ
            DeviceLog.objects.create(
                device=self,
                status=self.status,
                timestamp=self.last_changed
            )

    @property
    def current_power_draw(self):
        return self.power_watt if self.status else 0


class DeviceLog(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='logs')
    status = models.BooleanField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        state = "ON" if self.status else "OFF"
        return f"{self.device.name} turned {state} at {self.timestamp}"


class Alert(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert: {self.message}"