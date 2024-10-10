from rest_framework import serializers
from .models import Order, OrderItem, Payment, Shipment


# OrderItem Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price_at_order",
            "total_price",
        ]
        read_only_fields = ["id", "product_name", "total_price", "price_at_order"]


# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "order_number",
            "shipping_address",
            "billing_address",
            "total_amount",
            "status",
            "status_display",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = [
            "id",
            "user",
            "order_number",
            "total_amount",
            "status_display",
            "created_at",
            "updated_at",
        ]


# Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.order_number", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "order_number",
            "amount",
            "payment_method",
            "transaction_id",
            "status",
            "updated_at",
        ]
        read_only_fields = ["order_number", "updated_at"]


# Shipment Serializer
class ShipmentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.order_number", read_only=True)

    class Meta:
        model = Shipment
        fields = [
            "id",
            "order",
            "order_number",
            "tracking_number",
            "carrier",
            "status",
            "estimated_delivery",
            "shipped_at",
            "delivered_at",
        ]
        read_only_fields = ["order_number", "shipped_at", "delivered_at"]
