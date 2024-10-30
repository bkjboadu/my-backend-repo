from rest_framework.permissions import IsAuthenticated
import stripe, json
import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from .models import Order, StripePayment, PayPalPayment
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.views.generic import View
from paypalrestsdk import Payment
from rest_framework.views import APIView
from .paystack import verify_payment
from .tasks import process_order, send_order_confirmation_mail


# stripe payment setup
stripe.api_key = settings.STRIPE_SECRET_KEY
paystack_secret_key = settings.PAYSTACK_SECRET_KEY

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
headers = {
    "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    "Content-Type": "application/json",
}


class StripePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        order = get_object_or_404(Order, id=order_id)
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),
            currency="cad",
            payment_method_types=["card"],
        )
        return JsonResponse({"clientSecret": intent["client_secret"]})


class StripePaymentConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_exempt)
    def post(self, request):
        payment_intent_id = request.data.get("payment_intent_id")
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            stripe_charge_id = payment_intent.id
            stripe_intent_status = payment_intent.status
            amount_received = payment_intent.amount_received / 100
            print("Stripe_charge_id", stripe_charge_id)
            print("Stripe_intent_status", stripe_intent_status)
            print("Stripe_amount", amount_received)

            payment = StripePayment.objects.create(
                order_id=request.data.get("order_id"),
                stripe_charge_id=stripe_charge_id,
                amount=amount_received,
                status=stripe_intent_status,
            )

            return JsonResponse(
                {
                    "status": "success",
                    "payment_id": payment.id,
                    "message": "Your payment was successful!",
                }
            )

        except stripe.error.StripeError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)


# paypal payment setup
class PayPalPaymentView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        if order.payment_status == "paid":
            return JsonResponse({"details": "Order already paid for"})

        payment = Payment(
            {
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": request.build_absolute_uri(
                        reverse("paypal-payment-success")
                    ),
                    "cancel_url": request.build_absolute_uri(
                        reverse("paypal-payment-error")
                    ),
                },
                "transactions": [
                    {
                        "item_list": {
                            "items": [
                                {
                                    "name": f"Order {order.id}",
                                    "sku": str(order.id),
                                    "price": str(order.total_amount),
                                    "currency": "USD",
                                    "quantity": 1,
                                }
                            ]
                        },
                        "amount": {"total": str(order.total_amount), "currency": "USD"},
                        "description": f"Payment for Order {order.id}",
                    }
                ],
            }
        )

        if payment.create():
            approval_url = next(
                (link.href for link in payment.links if link.rel == "approval_url"),
                None,
            )
            if approval_url:
                return JsonResponse({"status": "success", "approval_url": approval_url})
            else:
                return JsonResponse(
                    {"status": "error", "message": "Approval URL not found."},
                    status=400,
                )
        else:
            return JsonResponse(
                {"status": "error", "message": "Failed to create PayPal payment."},
                status=400,
            )


class PaypalPaymentSuccessView(View):
    def get(self, request):
        payment_id = request.GET.get("paymentId")
        payer_id = request.GET.get("PayerID")
        try:
            payment = Payment.find(payment_id)
            if payment.execute({"payer_id": payer_id}):
                order_id = payment.transactions[0].item_list.items[0].sku
                order = get_object_or_404(Order, id=order_id)
                PayPalPayment.objects.create(
                    order=order,
                    paypal_transaction_id=payment_id,
                    amount=order.total_amount,
                    status="completed",
                )
                order.payment_status = "paid"
                order.save()

                process_order.delay(order_id)

                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Your payment was successful! Thank you for your order.",
                        "order_id": order.id,
                    }
                )
            else:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Payment execution failed. Please contact support.",
                    },
                    status=400,
                )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=500,
            )


class PayPalPaymentErrorView(View):
    def get(self, request):
        return JsonResponse(
            {
                "status": "error",
                "message": "Payment was canceled or an error occurred during the process.",
            },
            status=400,
        )


def initialize_transaction(email, amount):
    url = "https://api.paystack.co/transaction/initialize"
    data = {
        "email": email,
        "amount": amount * 100,
        "payment_channel": ["mobile_money"],
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


class InitializePaystackPaymentView(APIView):
    def post(self, request):
        try:
            user = request.user
            order_id = request.data.get("order_id")
            order = Order.objects.get(id=order_id, user=user)
            amount = order.total_amount
            email = user.email

            response = initialize_transaction(email, amount)

            if response["status"]:
                return JsonResponse(
                    {"authorization_url": response["data"]["authorization_url"]}
                )
            else:
                return JsonResponse(
                    {"error": "Payment initialization failed"}, status=400
                )
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)


class VerifyPayPalPaymentView(APIView):
    def post(self, request):
        reference = request.data.get("reference")
        response = verify_payment(reference)
        if response.get("status"):
            return JsonResponse(
                {"message": "Payment successful", "data": response["data"]}
            )
        else:
            return JsonResponse({"error": "Payment verification failed"}, status=400)


class PayPalPaymentCallBackView(APIView):
    def get(self, request):
        reference = request.GET.get("reference")

        response = verify_payment(reference)
        if response.get("status"):
            return JsonResponse(
                {"message": "Payment completed", "data": response["data"]}, status=200
            )
        else:
            return JsonResponse({"error": "Payment failed or incomplete"}, status=400)
