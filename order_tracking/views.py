from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from order_management.models import Order
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from order_tracking.serializers import OrderTrackingSerializer


class TrackOrderView(APIView):
    permission_class = [IsAuthenticated]

    def get(self, request, order_number):
        order = get_object_or_404(Order, id=order_number, user=request.user)
        serializer = OrderTrackingSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
        