from django.urls import path
from .views import (
    CartDetailView,
    CartUserListView,
    AddToCartView,
    UpdateCartItemView,
    ApplyPromotionCodeView,
    WishlistView,
    PromotionCodeListCreateView,
    PromotionCodeDetailView,
    CheckoutView,
)

urlpatterns = [
    path("cart/", CartDetailView.as_view(), name="cart-detail"),
    path("cart/user/", CartUserListView.as_view(), name="user-carts"),
    path("cart/add/<int:product_id>/", AddToCartView.as_view(), name="add-to-cart"),
    path(
        "cart/item/<int:item_id>/",
        UpdateCartItemView.as_view(),
        name="update-cart-item",
    ),
    path(
        "cart/apply-code/",
        ApplyPromotionCodeView.as_view(),
        name="apply-promotional-code",
    ),
    path("cart/checkout/", CheckoutView.as_view(), name="checkout"),
    path(
        "promotion-codes/",
        PromotionCodeListCreateView.as_view(),
        name="promotion-code-list-create",
    ),
    path(
        "promotion-codes/<int:pk>/",
        PromotionCodeDetailView.as_view(),
        name="promotion-code-detail",
    ),
    path("wishlist/", WishlistView.as_view(), name="wishlist"),
    path(
        "wishlist/add/<int:product_id>/", WishlistView.as_view(), name="add-to-wishlist"
    ),
    path(
        "wishlist/remove/<int:product_id>/",
        WishlistView.as_view(),
        name="remove-from-wishlist",
    ),
]
