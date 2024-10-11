from django.urls import path
from . import views

urlpatterns = [
    path(
        "stripe-create-payment-intent/<int:order_id>/",
        views.StripePaymentIntentView.as_view(),
        name="stripe-payment-intent",
    ),
    path("stripe-confirm-payment/", views.StripePaymentConfirmView, name="stripe-payment-success"),
    path('paypal-payment/<int:order_id>/', views.PayPalPaymentView.as_view(), name='paypal-payment'),
    path('paypal-payment-success/', views.PaypalPaymentSuccessView.as_view(), name='paypal-payment-success'),
    path('paypal-payment-error/', views.PaymentErrorView.as_view(), name='paypal-payment-error'),
]
