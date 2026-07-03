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
        পুরো অফিসের মোট কারেন্ট পাওয়ার লোড (Watts) এবং রুম ভিত্তিক ব্রেকডাউন হিসাব করার এপিআই
        """
        rooms = Room.objects.all()
        per_room = []
        total_office_watt = 0

        for room in rooms:
            # ওই রুমের যেসব ডিভাইস বর্তমানে ON (status=True) আছে
            active_devices = room.devices.filter(status=True) 
            # মডেলে ফিল্ডের নাম power_watt হওয়ায় d.power_watt ব্যবহার করা হয়েছে
            room_watt = sum(d.power_watt for d in active_devices)
            
            total_office_watt += room_watt
            per_room.append({
                "room": room.name,
                "slug": room.slug,
                "power_watt": room_watt
            })

        # আনুমানিক kWh হিসাব (২৪ ঘণ্টার জন্য একটি ডেমো এস্টিমেট)
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
        কোনো ডিভাইসের অন/অফ স্টেট টগল করার এপিআই এন্ডপয়েন্ট
        Expected JSON body: {"status": true} or {"status": false}
        """
        device = self.get_object()
        new_status = request.data.get('status')

        if new_status is None:
            return Response(
                {"error": "Status field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # মডেলের কাস্টম set_status মেথড কল করা হলো, যা অটোমেটিক লগও তৈরি করবে
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
    ডিভাইসগুলোর অন/অফ হওয়ার সাম্প্রতিক হিস্ট্রি বা লগ দেখার এপিআই (ঐচ্ছিক)
    """
    queryset = DeviceLog.objects.all()[:50] # সর্বশেষ ৫০টি লগ দেখাবে
    serializer_class = DeviceLogSerializer


# জ্যাঙ্গো টেমপ্লেট ভিউ (ড্যাশবোর্ড ফ্রন্টএন্ড রেন্ডার করার জন্য)
def dashboard(request):
    return render(request, 'devices/dashboard.html')