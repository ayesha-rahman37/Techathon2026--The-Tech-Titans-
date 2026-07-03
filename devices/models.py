from django.db import models

class Device(models.Model):
    DEVICE_TYPES = [
        ('fan', 'Fan'),
        ('light', 'Light'),
    ]
    
    ROOM_CHOICES = [
        ('drawing_room', 'Drawing Room'),
        ('work_room_1', 'Work Room 1'),
        ('work_room_2', 'Work Room 2'),
    ]
    
    name = models.CharField(max_length=50)
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES)
    room = models.CharField(max_length=20, choices=ROOM_CHOICES)
    status = models.BooleanField(default=False)  # True=ON, False=OFF
    power_draw = models.FloatField(default=0)  # Watts
    last_changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.room} - {self.name}"