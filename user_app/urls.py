from django.urls import path
from .views import CartView, AddToCartView, RemoveFromCartView

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart"),
    path("cart_add/", AddToCartView.as_view(), name="add_to_cart"),
    path(
        "cart/remove/<int:item_id>/",
        RemoveFromCartView.as_view(),
        name="remove_from_cart",
    ),
    # path('cart/update/<int:pk>/', UpdateCartView.as_view(), name='update_cart'),
]
