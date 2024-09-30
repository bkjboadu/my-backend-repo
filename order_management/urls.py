from django.urls import path
from .views import (
    CreateOrderView,
    OrderDetailView,
    UpdateOrderStatusView,
    PaymentView,
    ShipmentView,
    CancelOrderView,
    UserOrderListView
)

urlpatterns = [
    path('', CreateOrderView.as_view(), name='create-order'),

    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),

    path('list/', UserOrderListView.as_view(), name='order-list'),

    path('<int:order_id>/status/', UpdateOrderStatusView.as_view(), name='update-order-status'),

    path('<int:order_id>/payment/', PaymentView.as_view(), name='order-payment'),

    path('<int:order_id>/shipment/', ShipmentView.as_view(), name='order-shipment'),

    path('<int:order_id>/cancel/', CancelOrderView.as_view(), name='cancel-order'),
]
