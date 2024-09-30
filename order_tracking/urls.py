from django.urls import path
from .views import TrackOrderView

urlpatterns = [
    path('orders/<int:order_id>/', TrackOrderView.as_view(), name='track-order'),
]
