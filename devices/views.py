from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Room, Device, Alert, DeviceLog
from .serializers import RoomSerializer, DeviceSerializer, AlertSerializer, DeviceLogSerializer
from datetime import datetime

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
        API that calculates the total current power load (Watts) of the whole office and a room-wise breakdown
        """
        rooms = Room.objects.all()
        per_room = []
        total_office_watt = 0

        for room in rooms:
            # devices in this room that are currently ON (status=True)
            active_devices = room.devices.filter(status=True) 
            # the model field is named power_watt, so d.power_watt is used
            room_watt = sum(d.power_watt for d in active_devices)
            
            total_office_watt += room_watt
            per_room.append({
                "room": room.name,
                "slug": room.slug,
                "power_watt": room_watt
            })

        # estimated kWh (a demo estimate projected over 24 hours)
        estimated_kwh = (total_office_watt * 24) / 1000 

        return Response({
            "total_power_watt": total_office_watt,
            "per_room": per_room,
            "estimated_daily_usage_kwh": round(estimated_kwh, 2)
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
        API endpoint to toggle a device on/off
        Expected JSON body: {"status": true} or {"status": false}
        """
        device = self.get_object()
        new_status = request.data.get('status')

        if new_status is None:
            return Response(
                {"error": "Status field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # calls the model's custom set_status method, which also creates a log automatically
        device.set_status(bool(new_status))

        return Response({
            "message": f"{device.name} in {device.room.name} updated successfully.",
            "device_status": device.status
        }, status=status.HTTP_200_OK)


class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to fetch active office alerts for the dashboard panel.
    """
    queryset = Alert.objects.filter(is_active=True)
    serializer_class = AlertSerializer


class DeviceLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API to view recent on/off history/logs of devices (optional)
    """
    queryset = DeviceLog.objects.all()[:50] # shows the latest 50 logs
    serializer_class = DeviceLogSerializer


# Django template view (renders the dashboard frontend)
def dashboard(request):
    return render(request, 'devices/dashboard.html')