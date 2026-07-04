import time
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from devices.models import Device, Alert, Room


class Command(BaseCommand):
    help = "Simulates live office data and checks for anomalous activity alerts"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting live office simulation loop. Press Ctrl+C to exit."))

        while True:
            current_time = timezone.localtime(timezone.now())
            current_hour = current_time.hour

            # 1. Randomly toggle devices
            devices = list(Device.objects.all())
            if devices:
                target_devices = random.sample(devices, k=random.randint(1, 2))
                for device in target_devices:
                    device.set_status(not device.status)
                    self.stdout.write(
                        f"[{current_time.strftime('%H:%M:%S')}] Toggled "
                        f"{device.room.name} - {device.name} to {device.status}"
                    )

            is_after_hours = current_hour < 9 or current_hour >= 17

            # 2. Alert checks — once per room, not per device
            for room in Room.objects.all():
                room_devices = list(room.devices.all())
                active_devices = [d for d in room_devices if d.status]

                # Scenario A: any device ON after office hours
                if is_after_hours and active_devices:
                    exists = Alert.objects.filter(
                        room=room, message__startswith="After-hours:", is_active=True
                    ).exists()
                    if not exists:
                        msg = f"After-hours: {len(active_devices)} device(s) still ON in {room.name}"
                        Alert.objects.create(room=room, message=msg)
                        self.stdout.write(self.style.ERROR(f"ALERT: {msg}"))
                else:
                    # auto-resolve when office hours return or all devices are off
                    Alert.objects.filter(
                        room=room, message__startswith="After-hours:", is_active=True
                    ).update(is_active=False)

                # Scenario B: all devices continuously ON for more than 2 hours
                if room_devices and all(d.status for d in room_devices):
                    oldest_change = min(d.last_changed for d in room_devices)
                    duration = (current_time - oldest_change).total_seconds()
                    if duration >= 2 * 60 * 60:
                        msg = f"High Energy: all devices in {room.name} ON for 2+ hours"
                        exists = Alert.objects.filter(room=room, message=msg, is_active=True).exists()
                        if not exists:
                            Alert.objects.create(room=room, message=msg)
                            self.stdout.write(self.style.ERROR(f"ALERT: {msg}"))
                else:
                    Alert.objects.filter(
                        room=room, message__startswith="High Energy:", is_active=True
                    ).update(is_active=False)

            time.sleep(5)