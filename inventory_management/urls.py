from django.urls import path
from .views import (
    StoreListCreateView,
    StoreDetailView,
    ProductListCreateView,
    ProductDetailView,
    ProductImageListCreateView,
    ProductImageDetailView,
    StockEntryListCreateView,
    StockEntryDetailView,
    ProductReviewListCreateView,
    ProductReviewDetailView,
)

urlpatterns = [
    # Store URLs
    path("stores/", StoreListCreateView.as_view(), name="store-list-create"),
    path("stores/<int:pk>/", StoreDetailView.as_view(), name="store-detail"),
    # Category URLs
    # Product URLs
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    # Product Image URLs
    path(
        "product-images/",
        ProductImageListCreateView.as_view(),
        name="product-image-list-create",
    ),
    path(
        "product-images/<int:pk>/",
        ProductImageDetailView.as_view(),
        name="product-image-detail",
    ),
    # Stock Entry URLs
    path(
        "stock-entries/",
        StockEntryListCreateView.as_view(),
        name="stock-entry-list-create",
    ),
    path(
        "stock-entries/<int:pk>/",
        StockEntryDetailView.as_view(),
        name="stock-entry-detail",
    ),
    # Product Review URLs
    path(
        "products/<int:product_id>/reviews/",
        ProductReviewListCreateView.as_view(),
        name="product-review-list-create",
    ),
    path(
        "products/<int:product_id>/reviews/<int:pk>/",
        ProductReviewDetailView.as_view(),
        name="product-review-detail",
    ),
]
