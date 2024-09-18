from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from shop_app.models import Products
from rest_framework.permissions import IsAuthenticated


class CartView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        product = Products.objects.get(id=product_id)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, price=product.price)
        cart_item.quantity += int(quantity)
        cart_item.save()

        return Response({"message": "Item added to cart"}, status=status.HTTP_200_OK)

class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request, item_id):
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(cart=cart, id=item_id)
        cart_item.delete()

        return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)

