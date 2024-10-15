from celery import shared_task
from order_management.models import Order
from django.db import transaction
from django.forms.models import model_to_dict
import requests,os

@shared_task
def send_order_confirmation_mail(order_id):
    store_name = "Dropshop Electronics"
    sender = {"name": "bright", "email": "brbojr@gmail.com"}

    try:
        order = Order.objects.get(id=order_id)
    except order.DoesNotExist:
        print("Order not found")
        return


    print(order.user)
    subject = "Thank You for Your Order with Dropshop"

    message = f"""
        Hi {order.user.first_name},

        Thank you for shopping with us! We’re excited to let you know that we’ve received your order and it’s currently being processed. Here are the details of your order:

        Order Summary:
            • Order Number: {order.order_number}
            • Order Date: {order.created_at}
            • Shipping Address:
        {order.shipping_address}

        Items Ordered:
        {order.items.all()}  # Provide a formatted list of items here

        Total Amount: ${order.total_amount}

        What’s Next?

        We will notify you once your order is shipped and provide tracking information, so you can follow your order right to your doorstep. In the meantime, if you have any questions, feel free to reach out to our customer service team at {order.user.phone_number}.

        Thank you for choosing {store_name}. We hope you enjoy your purchase!

        Warm regards,
        The {store_name} Team
    """

    BREVO_API_KEY = os.getenv("BREVO_API_KEY")

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }

    data = {
        "sender": {"name": sender["name"], "email": sender["email"]},
        "to": [{"email": order.user.email, "name":order.user.first_name}],
        "subject": subject,
        "htmlContent": message,
    }

    url = "https://api.brevo.com/v3/smtp/email"

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email. Status code: {response.status_code}")
        print(f"Response: {response.text}")



@shared_task
def process_order(order_id):
    try:
        order = Order.objects.get(id=order_id)

        if not order.payment_status or order.payment_status != "paid":
            return {"status": "failed", "message": "Payment not completed"}

        # Update a stock and save order item in a transaction
        with transaction.atomic():
            for item in order.items.all():
                product = item.product

                if product.quantity_in_stock < item.quantity:
                    return {
                        "status": "failed",
                        "message": f"Insufficient stock for {product.name}",
                    }

                product.quantity_in_stock -= item.quantity
                product.save()

        order.status = "processing"
        send_order_confirmation_mail.delay(order_id)
        order.save()

        return {
            "status": "success",
            "message": f"Order {order.order_number} processed successfully",
        }
    except Order.DoesNotExist:
        return {"status": "failed", "message": "Order not found"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
