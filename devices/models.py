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
    name = models.CharField(max_length=50) # যেমন: "Fan 1", "Light 3"
    power_watt = models.PositiveIntegerField() # যেমন: ফ্যানের জন্য 60, লাইটের জন্য 15
    status = models.BooleanField(default=False) # True = ON, False = OFF
    last_changed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.room.name} - {self.name}"

    def set_status(self, new_status: bool):
        """ডিভাইসের স্টেট পরিবর্তন করার এবং লগ রাখার কাস্টম মেথড"""
        if new_status != self.status:
            self.status = new_status
            self.last_changed = timezone.now()
            self.save()
            
            # ডিভাইস অন/অফ হওয়ার হিস্ট্রি ট্র্যাক করার জন্য লগ তৈরি
            DeviceLog.objects.create(
                device=self,
                status=self.status,
                timestamp=self.last_changed
            )

    @property
    def current_power_draw(self):
        """ডিভাইসটি বর্তমানে কত ওয়াট বিদ্যুৎ টানছে তা সরাসরি পাওয়ার প্রোপার্টি"""
        return self.power_watt if self.status else 0


class DeviceLog(models.Model):
    """প্রতিবার ডিভাইস অন/অফ হলে তার হিস্ট্রি রাখার জন্য মডেল"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='logs')
    status = models.BooleanField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        state = "ON" if self.status else "OFF"
        return f"{self.device.name} turned {state} at {self.timestamp}"


class Alert(models.Model):
    """অফিস আওয়ারের বাইরে ডিভাইস অন থাকলে বা অ্যানোমালির জন্য অ্যালার্ট মডেল"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts') # নতুন ফিল্ড (ঐচ্ছিক)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert: {self.message}"