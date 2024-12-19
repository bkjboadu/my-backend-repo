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
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        cart = request.data.get('cart')

        if not cart:
            return Response(
                {"detail":"No cart data provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        # calculate the total amout from cart items
        total_amount = 0
        for item in cart:
            product = get_object_or_404(Product, id=item['product'])
            quantity = item['quantity']
            if quantity > product.quantity_in_stock:
                return Response({
                    "details":f"'{product.name}' is currently out of stock"
                }, status=status.HTTP_400_BAD_REQUEST)
            total_amount += quantity * product.price

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
    @method_decorator(csrf_exempt)
    def post(self, request):
        client_secret = request.data.get('clientSecret')
        payment_intent_id = client_secret.split('_secret_')[0]
        name = request.data.get('name')
        email = request.data.get('email')
        cart = request.data.get('cart')
        billing_address = request.data.get('billing_address', None)
        shipping_address = request.data.get('shipping_address')
        print(request.data)

        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            stripe_charge_id = payment_intent.id
            stripe_intent_status = payment_intent.status
            amount_received = payment_intent.amount_received / 100

            if stripe_intent_status == "succeeded":
                order = Order.objects.create(
                    name=name,
                    email=email,
                    shipping_address=shipping_address,
                    billing_address=billing_address,
                    total_amount=amount_received,
                )


                for item in cart:
                    product = get_object_or_404(Product, id=item["product"])
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
                # print(stripe.api_key)
                # print(settings.STRIPE_SECRET_KEY)
                # print(settings.STRIPE_PUBLISHABLE_KEY)

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
