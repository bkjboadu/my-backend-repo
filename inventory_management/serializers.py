from rest_framework.serializers import ModelSerializer, Serializer
from .models import Store,Supplier,StockEntry,Product,ProductImage,ProductVariant,Category,ProductReview

# Store Serializer
class StoreSerializer(ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"

# Category Serializer
class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

# Supplier Serializer
class SupplierSerializer(ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

# StockEntry Serializer
class StockEntrySerializer(ModelSerializer):
    class Meta:
        model = StockEntry
        fields = '__all__'

# Product Serializer
class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

# ProductVariant Serializer
class ProductVariantSerializer(ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'

# ProductImage Serializer
class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductReviewSerializer(ModelSerializer):
    class Meta:
        model = ProductReview
        fields = '__all__'
