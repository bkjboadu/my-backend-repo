from django.urls import path
from . import views

urlpatterns = [
    path(
        "stripe-confirm-payment/",
        views.StripePaymentConfirmView.as_view(),
        name="stripe-payment-success",
    ),
    path(
        "stripe-create-payment-intent/",
        views.StripePaymentIntentView.as_view(),
        name="stripe-payment-intent",
    ),
    # path(
    #     "paypal-payment/<int:order_id>/",
    #     views.PayPalPaymentView.as_view(),
    #     name="paypal-payment",
    # ),
    # path(
    #     "paypal-payment-success/",
    #     views.PaypalPaymentSuccessView.as_view(),
    #     name="paypal-payment-success",
    # ),
    # path(
    #     "paypal-payment-error/",
    #     views.PayPalPaymentErrorView.as_view(),
    #     name="paypal-payment-error",
    # ),
]
