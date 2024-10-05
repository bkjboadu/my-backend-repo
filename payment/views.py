import stripe, json
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order, StripePayment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_payment_intent(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    intent = stripe.PaymentIntent.create(
        amount=int(order.total_amount * 100),
        currency="cad",
        payment_method_types=["card"],
        description=f"Payment for Order {order_id}",
    )

    return JsonResponse({"client_secret": intent.client_secret, "order_id": order_id})


@csrf_exempt
def confirm_payment(request):
    if request.method == "POST":
        try:
            # Check if JSON data is sent
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST

            order_id = data.get("order_id")
            payment_intent_id = data.get("payment_intent_id")

            if not order_id or not payment_intent_id:
                return JsonResponse(
                    {"message": "Missing order_id or payment_intent_id"}, status=400
                )

            # Fetch the order and the payment intent details
            order = get_object_or_404(Order, id=order_id)
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status == "succeeded":
                # Payment was successful, update the order status
                StripePayment.objects.create(
                    order=order,
                    stripe_charge_id=intent.id,
                    amount=intent.amount / 100,
                    status="succeeded",
                )
                order.payment_status = "paid"
                order.save()
                return JsonResponse({"message": "Payment successful"}, status=200)

            else:
                return JsonResponse(
                    {
                        "message": "Payment not completed",
                        "payment_status": intent.status,
                        "required_action": intent.next_action,  # Optional, if additional action needed
                        "error_details": intent.last_payment_error,  # Optional, details of any error
                    },
                    status=400,
                )

        except stripe.error.StripeError as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data"}, status=400)

        except Exception as e:
            return JsonResponse({"message": f"Unexpected error: {str(e)}"}, status=500)

    return JsonResponse({"message": "Invalid request method"}, status=400)
