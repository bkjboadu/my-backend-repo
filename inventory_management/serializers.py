from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    SerializerMethodField,
)
from .models import (
    Store,
    Supplier,
    StockEntry,
    Product,
    ProductImage,
    ProductVariant,
    Category,
    ProductReview,
    VariantImage,
)
from cart_management.models import Wishlist


class ProductReviewSerializer(ModelSerializer):
    class Meta:
        model = ProductReview
        fields = "__all__"
        read_only_fields = ("product", "user", "created_at", "updated_at")


class VariantImageSerializer(ModelSerializer):
    class Meta:
        model = VariantImage
        fields = "__all__"


# ProductVariant Serializer
class ProductVariantSerializer(ModelSerializer):
    product_variant_images = VariantImageSerializer(many=True,read_only=True)

    class Meta:
        model = ProductVariant
        fields = "__all__"


# ProductImage Serializer
class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


# Product Serializer
class ProductSerializer(ModelSerializer):
    reviews = ProductReviewSerializer(many=True,read_only=True)
    product_images = ProductImageSerializer(many=True,read_only=True)
    is_in_wishlist = SerializerMethodField()

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
                    "category",
                    "supplier",
                    "is_in_wishlist",
                    "reviews",
                    "product_images",
                ]

    def get_is_in_wishlist(self,obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Wishlist.objects.filter(user=user,product=obj).exists()
        return False


# Category Serializer
class CategorySerializer(ModelSerializer):
    # products = ProductSerializer(many=True,read_only=True)
    products = SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

    def get_products(self, obj):
        # Use filtered products if available
        products = self.context.get("filtered_products", obj.products)
        return ProductSerializer(products, many=True).data


# Store Serializer
class StoreSerializer(ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Store
        fields = "__all__"


# Supplier Serializer
class SupplierSerializer(ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


# StockEntry Serializer
class StockEntrySerializer(ModelSerializer):
    class Meta:
        model = StockEntry
        fields = "__all__"
