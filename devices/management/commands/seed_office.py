from django.core.management.base import BaseCommand
from devices.models import Room, Device

class Command(BaseCommand):
    help = "Seeds the database with initial rooms and 18 devices as per requirements"

    def handle(self, *args, **options):
        # Define the 3 required rooms
        rooms_data = [
            {"name": "Drawing Room", "slug": "drawing_room"},
            {"name": "Work Room 1", "slug": "work_room_1"},
            {"name": "Work Room 2", "slug": "work_room_2"},
        ]

        self.stdout.write("Seeding database...")

        for room_info in rooms_data:
            room, created = Room.objects.get_or_create(
                slug=room_info["slug"], 
                defaults={"name": room_info["name"]}
            )
            
            if created:
                self.stdout.write(f"Created room: {room.name}")
                
                # Seed 2 Fans for this room (60W each)
                for i in range(1, 3):
                    Device.objects.create(
                        room=room,
                        device_type=Device.FAN,
                        name=f"Fan {i}",
                        power_watt=60,
                        status=False
                    )
                
                # Seed 3 Lights for this room (15W each)
                for i in range(1, 4):
                    Device.objects.create(
                        room=room,
                        device_type=Device.LIGHT,
                        name=f"Light {i}",
                        power_watt=15,
                        status=False
                    )
                self.stdout.write(f"-> Added 2 Fans and 3 Lights to {room.name}")
            else:
                self.stdout.write(f"Room {room.name} already exists. Skipping.")

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))