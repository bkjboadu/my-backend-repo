from django.urls import path
from . import views

urlpatterns = [
    path('stripe-create-payment-intent/<int:order_id>/', views.create_stripe_payment_intent, name='create-stripe-payment-intent'),
    path('stripe-confirm-payment/', views.confirm_payment, name='confirm-payment'),
]
