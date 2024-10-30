from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from .models import Cart, CartItem, PromotionCode, Wishlist
from inventory_management.models import Product
from inventory_management.serializers import ProductSerializer


class PromotionCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionCode
        fields = "__all__"

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price_at_addition",
            "total_price",
        ]


class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    promotion_code = PromotionCodeSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"
        read_only_fields = ["id", "user"]

    def get_items(self, obj):
        cart_items = CartItem.objects.filter(cart=obj)
        return CartItemSerializer(cart_items, many=True).data


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        exclude = ['id']
