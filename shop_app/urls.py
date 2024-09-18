from django.urls import path
from .views import (CategoryDetailView, ParentCategoryCreateView, ParentCategoryDetailView,
                    ProductDetailView, ProductImageListCreateView, ProductListCreateView, 
                    CategoryListCreateAPIView, TagsListCreateView, BrandListCreateView)

urlpatterns = [
    path('create_products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('product_images/', ProductImageListCreateView.as_view(), name='product-image-create'),
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('tags/', TagsListCreateView.as_view(), name='tags'),
    path('brands/', BrandListCreateView.as_view(), name='create-brands'),
    path('parent_categories/<int:pk>/', ParentCategoryDetailView.as_view(), name='parent-category-detail'),
    path('parent_categories/', ParentCategoryCreateView.as_view(), name='parent-category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('parent_category/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
]