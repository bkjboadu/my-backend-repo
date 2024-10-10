from django.urls import path
# from . import views
from .views import StripeConfirmPayment,StripePayment,InitializePaystackPaymentView,VerifyPaymentView, PaymentCallBackView
# urlpatterns = [
#     path(
#         "stripe-create-payment-intent/<int:order_id>/",
#         views.create_stripe_payment_intent,
#         name="create-stripe-payment-intent",
#     ),
#     path("stripe-confirm-payment/", views.confirm_payment, name="confirm-payment"),
# ]

urlpatterns = [
    path("stripe-create-payment-intent<int:order_id>/", StripePayment.as_view(), name="create-stripe-payment-intent"),
    path("confirm-stripe-payment/", StripeConfirmPayment.as_view(), name="confirm-payment-stripe"),
    path("paystack/initialize/", InitializePaystackPaymentView.as_view(), name="initialize-paystack-payment"),
    path("paystack/verify/", VerifyPaymentView.as_view(), name="verify-payment"),
    path("paystack/callback/", PaymentCallBackView.as_view(), name="payment-callback"),  
]
