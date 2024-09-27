from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order, OrderItem, Payment, Shipment
from inventory_management.models import Product
from .serializers import (
    OrderSerializer,
    OrderItemSerializer,
    PaymentSerializer,
    ShipmentSerializer
)
from django.shortcuts import get_object_or_404
from django.utils import timezone

# Create a New Order
class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = request.data.get('cart')  # Assuming you pass the cart data from the frontend
        if not cart:
            return Response({"detail": "No cart data provided."}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=request.user,
            shipping_address=request.data.get('shipping_address'),
            billing_address=request.data.get('billing_address', None)
        )

        total_amount = 0

        # Create Order Items from cart data
        for item in cart:
            product = get_object_or_404(Product, id=item['product_id'])
            quantity = item['quantity']
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_order=product.price
            )
            total_amount += order_item.total_price

        order.total_amount = total_amount
        order.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


# View, Update, or Cancel an Order
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status in ['shipped', 'delivered']:
            return Response({"detail": "Cannot cancel an order that has been shipped or delivered."}, status=status.HTTP_400_BAD_REQUEST)

        instance.status = 'canceled'
        instance.save()
        return Response({"detail": "Order canceled successfully."}, status=status.HTTP_200_OK)


# List all orders for the authenticated user
class UserOrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# Admin: List all orders
class AdminOrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


# Update Order Status (Admin Only)
class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get('status')

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()
        return Response({"detail": f"Order status updated to {new_status}."}, status=status.HTTP_200_OK)


# Handle Payments
class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.payment_method:
            return Response({"detail": "Payment already made for this order."}, status=status.HTTP_400_BAD_REQUEST)

        payment_data = {
            'order': order.id,
            'amount': order.total_amount,
            'payment_method': request.data.get('payment_method'),
            'status': 'completed',
            'transaction_id': f'TRANSACTION-{order_id}-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        }


        serializer = PaymentSerializer(data=payment_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Shipment Details and Tracking (Admin Only)
class ShipmentView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        if not order.payment or order.payment.status != 'completed':
            return Response({"detail": "Cannot create a shipment for unpaid orders."}, status=status.HTTP_400_BAD_REQUEST)

        shipment_data = {
            'order': order.id,
            'tracking_number': request.data.get('tracking_number'),
            'carrier': request.data.get('carrier'),
            'estimated_delivery': request.data.get('estimated_delivery'),
            'status': 'in_transit',
        }

        serializer = ShipmentSerializer(data=shipment_data)
        if serializer.is_valid():
            serializer.save()
            order.status = 'shipped'
            order.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, order_id):
        shipment = get_object_or_404(Shipment, order__id=order_id)
        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_200_OK)



class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        # Get the specific order for the authenticated user
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Check if the order can be canceled (e.g., check if it's not already shipped or completed)
        if order.status in ['shipped', 'completed']:
            return Response({"detail": "This order cannot be canceled as it is already shipped or completed."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Update the order status to 'canceled'
        order.status = 'canceled'
        order.save()

        return Response({"detail": f"Order {order.id} has been successfully canceled."}, status=status.HTTP_200_OK)
