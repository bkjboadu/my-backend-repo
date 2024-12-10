from rest_framework.serializers import ModelSerializer
from .models import (
    Store,
    StockEntry,
    Product,
    ProductImage,
    ProductReview,
)


class ProductReviewSerializer(ModelSerializer):
    class Meta:
        model = ProductReview
        fields = "__all__"
        read_only_fields = ("product", "user", "created_at", "updated_at")


class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class ProductSerializer(ModelSerializer):
    reviews = ProductReviewSerializer(many=True, read_only=True)
    product_images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "sku",
            "price",
            "quantity_in_stock",
            "created_at",
            "updated_at",
            "is_active",
            "store",
            "reviews",
            "product_images",
        ]


class StoreSerializer(ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


class StockEntrySerializer(ModelSerializer):
    class Meta:
        model = StockEntry
        fields = "__all__"
