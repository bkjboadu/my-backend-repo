from rest_framework import serializers
from order_management.models import Order, Shipment

from rest_framework import serializers

from order_management.serializers import OrderItemSerializer
from order_management.models import Order, Shipment


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = [
            "tracking_number",
            "carrier",
            "status",
            "estimated_delivery",
            "shipped_at",
            "delivered_at",
        ]


class OrderTrackingSerializer(serializers.ModelSerializer):
    shipment = ShipmentSerializer()  # nested Shipment serializer
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "order_number",
            "status",
            "created_at",
            "updated_at",
            "items",
            "shipment",
        ]
