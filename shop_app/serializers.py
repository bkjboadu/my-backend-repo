from rest_framework import serializers
from .models import (Brand, Category, ProductImage, ProductReview, Products, Pricing, Tags)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'description','parent_category')

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('name', 'description')

class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    description = serializers.CharField(max_length=500)

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be positive.")
        return value

    class Meta:
        model = Products
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','product','image','alt_text']

    def create(self, validated_data):
        return ProductImage.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.alt_text = validated_data.get('alt_text', instance.alt_text)
        instance.save()
        return instance

# 'created_at', 'updated_at'

class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields = ['id', 'product_name', 'price', 'discount_price', 'currency']

class TagsSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Tags
        fields = ['id', 'product', 'tag']


class ProductReviewSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)	
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'rating', 'review', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


