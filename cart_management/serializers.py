from rest_framework import serializers
from .models import Cart, CartItem, PromotionCode, Wishlist


class PromotionCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionCode
        fields = "__all__"


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


class WishlistSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Wishlist
        fields = "__all__"
