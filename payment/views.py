from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

import stripe
from paypalrestsdk import Payment

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse


from .models import StripePayment, PayPalPayment
from .paystack import verify_payment
from .tasks import process_order, send_order_confirmation_mail
from inventory_management.models import Product
from order_management.models import Order, OrderItem



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
    def post(self,request, *args, **kwargs):
        cart = request.data.get('cart')
        shipping_address = request.data.get('shipping_address')
        billing_address = request.data.get('billing_address')

        if not cart:
            return Response(
                {"detail":"No cart data provided"},status=status.HTTP_400_BAD_REQUEST
            )

        # calculate the total amout from cart items
        total_amount = 0
        for item in cart:
            product = get_object_or_404(Product, id=item['product_id'])
            quantity = item['quantity']
            if quantity > product.quantity_in_stock:
                return Response({
                    "details":f"Only {product.quantity_in_stock} units of '{product.name}' are available in stock"
                },status=status.HTTP_400_BAD_REQUEST)
            total_amount  += quantity * product.price

        # Create Stripe Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),
            currency="cad",
            payment_method_types=["card"],
        )
        return Response({
            "clientSecret": intent["client_secret"],
            "payment_intent_id": intent['client_secret'].split('_secret_')[0]
        },
        status=status.HTTP_200_OK)



class StripePaymentConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_exempt)
    def post(self, request):
        client_secret = request.data.get('clientSecret')
        payment_intent_id = client_secret.split('_secret_')[0]
        cart = request.data.get('cart')
        billing_address = request.data.get('billing_address',None)
        shipping_address = request.data.get('shipping_address')

        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            stripe_charge_id = payment_intent.id
            stripe_intent_status = payment_intent.status
            amount_received = payment_intent.amount_received / 100
            # print("Stripe_charge_id", stripe_charge_id)
            # print("Stripe_intent_status", stripe_intent_status)
            # print("Stripe_amount", amount_received)

            if stripe_intent_status == "succeeded":
                order = Order.objects.create(
                            user=request.user,
                            shipping_address=shipping_address,
                            billing_address=billing_address,
                            total_amount=amount_received,
                        )


                for item in cart:
                    product = get_object_or_404(Product, id=item["product_id"])
                    quantity = item["quantity"]

                    product.quantity_in_stock -= quantity
                    product.save()

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price_at_order=product.price,
                    )

                order.payment_status = "paid"
                order.status = "processing"
                order.save()

                StripePayment.objects.create(
                    order=order,
                    stripe_charge_id=stripe_charge_id,
                    amount=amount_received,
                    status=stripe_intent_status,
                )

                send_order_confirmation_mail(order.id)

                return Response(
                    {
                        "status": "success",
                        "order_id": order.id,
                        "message": "Your payment was successful!",
                    }
                )
            else:
                return Response(
                    {
                        "message":"Payment did not succeed"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except stripe.error.StripeError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# paypal payment setup
class PayPalPaymentView(APIView):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        if order.payment_status == "paid":
            return Response({"details": "Order already paid for"})

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
                return Response({"status": "success", "approval_url": approval_url},status=status.HTTP_200_OK)
            else:
                return Response(
                    {"status": "error", "message": "Approval URL not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"status": "error", "message": "Failed to create PayPal payment."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PaypalPaymentSuccessView(APIView):
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

                return Response(
                    {
                        "status": "success",
                        "message": "Your payment was successful! Thank you for your order.",
                        "order_id": order.id,
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "status": "error",
                        "message": "Payment execution failed. Please contact support.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PayPalPaymentErrorView(APIView):
    def get(self, request):
        return Response(
            {
                "status": "error",
                "message": "Payment was canceled or an error occurred during the process.",
            },
            status=status.HTTP_400_BAD_REQUEST,
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
                return Response(
                    {"authorization_url": response["data"]["authorization_url"]},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Payment initialization failed"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyPayPalPaymentView(APIView):
    def post(self, request):
        reference = request.data.get("reference")
        response = verify_payment(reference)
        if response.get("status"):
            return Response(
                {"message": "Payment successful", "data": response["data"]},
                status=status.HTTP_200_OK
            )
        else:
            return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)


class PayPalPaymentCallBackView(APIView):
    def get(self, request):
        reference = request.GET.get("reference")

        response = verify_payment(reference)
        if response.get("status"):
            return Response(
                {"message": "Payment completed", "data": response["data"]}, status=status.HTTP_200_OK
            )
        else:
            return Response({"error": "Payment failed or incomplete"}, status=status.HTTP_200_OK)
