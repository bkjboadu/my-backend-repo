from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from order_management.models import Order
from .models import OrderTracking
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from order_tracking.serializers import OrderTrackingSerializer

#for user
class TrackOrderView(APIView):
    permission_class = [IsAuthenticated]

    def get(self, request, order_number):
        order = get_object_or_404(Order, id=order_number, user=request.user)
        serializer = OrderTrackingSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


#for admin
class OrderTrackingDetailView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, tracking_number):
        tracking = OrderTracking.objects.get(tracking_number=tracking_number)
        serializer = OrderTrackingSerializer(tracking)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpdateOrderTrackingStatus(APIView):
    permission_classes = [IsAdminUser]
    def patch(self, request, tracking_number):
        tracking = OrderTracking.objects.get(tracking_number=tracking_number)
        serializer = OrderTrackingSerializer(tracking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

