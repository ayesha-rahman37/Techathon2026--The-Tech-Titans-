from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Room, Device, Alert
from .serializers import RoomSerializer, DeviceSerializer, AlertSerializer


class RoomViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows rooms to be viewed or edited.
    Includes a custom action to get the total power consumption of the office.
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    @action(detail=False, methods=['get'])
    def office_power(self, request):
        """
        Total power drawn across the whole office plus a per-room breakdown.
        """
        per_room = []
        total_office_watt = 0

        for room in Room.objects.all():
            room_watt = sum(d.current_power_draw for d in room.devices.all())
            total_office_watt += room_watt
            per_room.append({
                "room": room.name,
                "slug": room.slug,
                "power_watt": room_watt,
            })

        estimated_kwh = (total_office_watt * 8) / 1000  # rough demo estimate

        return Response({
            "total_power_watt": total_office_watt,
            "per_room": per_room,
            "estimated_daily_usage_kwh": round(estimated_kwh, 2),
        }, status=status.HTTP_200_OK)


class DeviceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows devices to be viewed or updated.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """
        Turn a device ON or OFF.
        Expected JSON body: {"status": true} or {"status": false}
        """
        device = self.get_object()
        new_status = request.data.get('status')

        if new_status is None:
            return Response(
                {"error": "Status field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        device.set_status(bool(new_status))

        return Response({
            "message": f"{device.name} in {device.room.name} updated successfully.",
            "device_status": device.status
        }, status=status.HTTP_200_OK)


class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to fetch active office alerts.
    """
    queryset = Alert.objects.filter(is_active=True)
    serializer_class = AlertSerializer