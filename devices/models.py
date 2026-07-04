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
    name = models.CharField(max_length=50) # e.g. "Fan 1", "Light 3"
    power_watt = models.PositiveIntegerField() # e.g. 60 for a fan, 15 for a light
    status = models.BooleanField(default=False) # True = ON, False = OFF
    last_changed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.room.name} - {self.name}"

    def set_status(self, new_status: bool):
        """Custom method to change device state and keep a log"""
        if new_status != self.status:
            self.status = new_status
            self.last_changed = timezone.now()
            self.save()
            
            # create a log entry to track device on/off history
            DeviceLog.objects.create(
                device=self,
                status=self.status,
                timestamp=self.last_changed
            )

    @property
    def current_power_draw(self):
        """Property that returns how many watts the device is drawing right now"""
        return self.power_watt if self.status else 0


class DeviceLog(models.Model):
    """Model that keeps history every time a device turns on/off"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='logs')
    status = models.BooleanField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        state = "ON" if self.status else "OFF"
        return f"{self.device.name} turned {state} at {self.timestamp}"


class Alert(models.Model):
    """Alert model for devices left ON outside office hours or other anomalies"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts') # optional field
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert: {self.message}"