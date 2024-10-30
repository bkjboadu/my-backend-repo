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
    Category,
    ProductReview,
)
from cart_management.models import Wishlist


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

    def get_is_in_wishlist(self, obj):
        from cart_management.serializers import WishlistSerializer

        request = self.context.get("request")
        if isinstance(self.parent, WishlistSerializer):
            return True

        if not request:
            return False

        user = request.user
        print(user)
        if user.is_authenticated:
            return Wishlist.objects.filter(user=user, product=obj).exists()
        return False


class CategorySerializer(ModelSerializer):
    products = SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

    def get_products(self, obj):
        products = self.context.get("filtered_products", obj.products)
        return ProductSerializer(products, many=True, context=self.context).data


class StoreSerializer(ModelSerializer):
    categories = SerializerMethodField()

    class Meta:
        model = Store
        fields = "__all__"

    def get_categories(self,obj):
        context = self.context
        categories = obj.categories.all()
        return CategorySerializer(categories,context=context).data


class SupplierSerializer(ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class StockEntrySerializer(ModelSerializer):
    class Meta:
        model = StockEntry
        fields = "__all__"
