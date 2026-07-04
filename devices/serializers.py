from rest_framework import serializers
from .models import Room, Device, DeviceLog, Alert


class DeviceSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.name', read_only=True)
    room_slug = serializers.CharField(source='room.slug', read_only=True)
    current_power = serializers.IntegerField(source='current_power_draw', read_only=True)

    class Meta:
        model = Device
        fields = [
            'id', 'name', 'device_type', 'room', 'room_name', 'room_slug',
            'power_watt', 'current_power', 'status', 'last_changed',
        ]


class RoomSerializer(serializers.ModelSerializer):
    devices = DeviceSerializer(many=True, read_only=True)
    total_power_draw = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'slug', 'devices', 'total_power_draw']

    def get_total_power_draw(self, obj):
        # total power of all devices currently ON in this room
        return sum(device.current_power_draw for device in obj.devices.all())


class DeviceLogSerializer(serializers.ModelSerializer):
    """Serializer for showing device on/off history in the frontend or bot"""
    device_name = serializers.CharField(source='device.name', read_only=True)

    class Meta:
        model = DeviceLog
        fields = ['id', 'device', 'device_name', 'status', 'timestamp']


class AlertSerializer(serializers.ModelSerializer):
    room_name = serializers.SerializerMethodField()
    device_name = serializers.CharField(source='device.name', read_only=True) # added field

    class Meta:
        model = Alert
        fields = ['id', 'room', 'room_name', 'device', 'device_name', 'message', 'created_at', 'is_active']

    def get_room_name(self, obj):
        return obj.room.name if obj.room else None