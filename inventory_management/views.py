from django.shortcuts import render
from rest_framework import generics
from .models import Brand, Category, ParentCategory, ProductImage, Products, Tags
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ParentCategorySerializer,
    ProductImageSerializer,
    ProductSerializer,
    TagsSerializer,
)
from inventory_management import serializers


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer


class ParentCategoryCreateView(generics.ListCreateAPIView):
    queryset = ParentCategory.objects.all()
    serializer_class = ParentCategorySerializer


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def perform_create(self, serializer):
        parent_category_name = self.request.data.get("parent_category")
        if parent_category_name:
            try:
                parent_category = ParentCategory.objects.get(pk=parent_category_name)
                serializer.save(parent_category=parent_category)
            except ParentCategory.DoesNotExist:
                raise serializers.ValidationError("Parent category does not exist.")
        else:
            serializer.save()


class BrandListCreateView(generics.ListCreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class ProductImageListCreateView(generics.ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


class TagsListCreateView(generics.ListCreateAPIView):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer


class ParentCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ParentCategory.objects.all()
    serializer_class = ParentCategorySerializer
