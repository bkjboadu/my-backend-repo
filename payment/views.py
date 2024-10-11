import stripe, json
from django.conf import settings
from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Order, StripePayment,PayPalPayment
from django.urls import reverse
from django.views.generic import View
from paypalrestsdk import Payment


# stripe payment setup
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentIntentView(View):
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        order_id = request.POST.get("order_id")
        order = get_object_or_404(Order, id=order_id)

        # Create a Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),
            currency="cad",
            payment_method_types=["card"],
        )

        return JsonResponse({
            "clientSecret": intent["client_secret"]
        })

class StripePaymentConfirmView(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        payment_intent_id = request.POST.get("payment_intent_id")

        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            stripe_payment_id = payment_intent.id
            amount_received = payment_intent.amount_received / 100  # Convert cents to dollars

            payment = StripePayment.objects.create(
                order_id=request.POST.get("order_id"),
                stripe_payment_id=stripe_payment_id,
                amount=amount_received,
                status=payment_intent.status
            )

            return JsonResponse({
                "status": "success",
                "payment_id": payment.id,
                "message": "Your payment was successful!"
            })

        except stripe.error.StripeError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)


# paypal payment setup
class PayPalPaymentView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        # Setup PayPal Payment
        payment = Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri(reverse('payment-success')),
                "cancel_url": request.build_absolute_uri(reverse('payment-error'))
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"Order {order.id}",
                        "sku": str(order.id),
                        "price": str(order.total_amount),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(order.total_amount),
                    "currency": "USD"
                },
                "description": f"Payment for Order {order.id}"
            }]
        })

        # Attempt to create payment
        if payment.create():
            approval_url = next((link.href for link in payment.links if link.rel == "approval_url"), None)
            if approval_url:
                return JsonResponse({
                    "status": "success",
                    "approval_url": approval_url
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Approval URL not found."
                }, status=400)
        else:
            return JsonResponse({
                "status": "error",
                "message": "Failed to create PayPal payment."
            }, status=400)

class PaypalPaymentSuccessView(View):
    def get(self, request):
        payment_id = request.GET.get('paymentId')
        payer_id = request.GET.get('PayerID')
        try:
            payment = Payment.find(payment_id)
            if payment.execute({"payer_id": payer_id}):
                order_id = payment.transactions[0].item_list.items[0].sku
                order = get_object_or_404(Order, id=order_id)
                PayPalPayment.objects.create(
                    order=order,
                    paypal_transaction_id=payment_id,
                    amount=order.total_amount,
                    status='completed'
                )
                return JsonResponse({
                    "status": "success",
                    "message": "Your payment was successful! Thank you for your order.",
                    "order_id": order.id
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Payment execution failed. Please contact support."
                }, status=400)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }, status=500)


class PaymentErrorView(View):
    def get(self, request):
        return JsonResponse({
            "status": "error",
            "message": "Payment was canceled or an error occurred during the process."
        }, status=400)
