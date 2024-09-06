from django.urls import path
from .views import ProductImageCreateView, ProductListCreateView

urlpatterns = [
    path('create_products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('product_images/', ProductImageCreateView.as_view(), name='product-image-create'),
]