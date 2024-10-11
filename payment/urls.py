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
    path('paypal-payment-error/', views.PayPalPaymentErrorView.as_view(), name='paypal-payment-error'),
    path("paystack/initialize/", views.InitializePaystackPaymentView.as_view(), name="initialize-paystack-payment"),
    path("paystack/verify/", views.VerifyPayPalPaymentView.as_view(), name="verify-payment"),
    path("paystack/callback/", views.PayPalPaymentCallBackView.as_view(), name="payment-callback"),
]
