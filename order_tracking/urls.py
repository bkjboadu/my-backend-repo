from django.urls import path
from .views import TrackOrderView, OrderTrackingDetailView,UpdateOrderTrackingStatus

urlpatterns = [
    path('track_orders/<int:order_id>/', TrackOrderView.as_view(), name='track-order'),
    path('admin_track_orders/<str:tracking_number>/', OrderTrackingDetailView.as_view(), name='admin-track-orders'),
    path('update_tracked_orders/<str:tracking_number>/', UpdateOrderTrackingStatus.as_view(), name='update-tracked-orders')

from .views import TrackOrderView, OrderTrackingDetailView, UpdateOrderTrackingStatus

urlpatterns = [
    path("track_orders/<int:order_id>/", TrackOrderView.as_view(), name="track-order"),
    path(
        "admin_track_orders/<str:tracking_number>/",
        OrderTrackingDetailView.as_view(),
        name="admin-track-orders",
    ),
    path(
        "update_tracked_orders/<str:tracking_number>/",
        UpdateOrderTrackingStatus.as_view(),
        name="update-tracked-orders",
    ),

