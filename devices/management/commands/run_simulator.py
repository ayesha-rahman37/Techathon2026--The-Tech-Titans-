import time
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from devices.models import Room, Device, Alert

class Command(BaseCommand):
    help = 'Simulates real-time office devices usage and handles background alerts'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Device simulator started successfully...'))

        while True:
            # ১. র্যান্ডমলি যেকোনো ডিভাইসের স্টেট টগল (ON/OFF) করা
            devices = list(Device.objects.all())
            if devices:
                # যেকোনো ১ বা ২টা র্যান্ডম ডিভাইস সিলেক্ট করা
                sampled_devices = random.sample(devices, min(len(devices), random.randint(1, 2)))
                for device in sampled_devices:
                    new_status = random.choice([True, False])
                    device.set_status(new_status)
                    self.stdout.write(f"Updated: {device.room.name} - {device.name} is now {'ON' if new_status else 'OFF'}")

            # ২. অনিয়ম বা অ্যানোমালি চেক করা
            self.check_for_anomalies()

            # প্রতি ১০ সেকেন্ড পর পর লুপটি ঘুরবে
            time.sleep(10)

    def check_for_anomalies(self):
        now = timezone.now()
        local_time = timezone.localtime(now)
        current_hour = local_time.hour

        # কন্ডিশন ১: অফিস আওয়ারের বাইরে (9 AM - 5 PM এর বাইরে) ডিভাইস অন থাকলে অ্যালার্ট [cite: 194]
        if current_hour < 9 or current_hour >= 17:
            active_devices = Device.objects.filter(status=True)
            for device in active_devices:
                msg = f"Anomalous Activity: '{device.name}' left ON in {device.room.name} outside office hours."
                if not Alert.objects.filter(device=device, message=msg, is_active=True).exists():
                    Alert.objects.create(room=device.room, device=device, message=msg)
                    self.stdout.write(self.style.WARNING(f"ALERT: {msg}"))

        # কন্ডিশন ২: কোনোルームের সব ডিভাইস টানা ২ ঘণ্টার বেশি অন থাকলে অ্যালার্ট [cite: 194]
        rooms = Room.objects.all()
        for room in rooms:
            total_devices_count = room.devices.count()
            active_devices_count = room.devices.filter(status=True).count()

            # যদি রুমের সবগুলো ডিভাইস একসাথে অন থাকে
            if total_devices_count > 0 and active_devices_count == total_devices_count:
                # চেক করা হচ্ছে সব ডিভাইসগুলোর লাস্ট চেঞ্জ টাইম ২ ঘণ্টার বেশি পুরোনো কি না [cite: 194]
                old_devices = room.devices.filter(status=True, last_changed__lt=now - timezone.timedelta(hours=2))
                if old_devices.count() == total_devices_count:
                    msg = f"Energy Waste Alert: All devices in {room.name} have been running continuously for over 2 hours!"
                    if not Alert.objects.filter(room=room, message=msg, is_active=True).exists():
                        Alert.objects.create(room=room, message=msg)
                        self.stdout.write(self.style.WARNING(f"ALERT: {msg}"))