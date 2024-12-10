import requests, os
from celery import shared_task
from order_management.models import Order
from django.db import transaction


@shared_task
def send_order_confirmation_mail(order_id):
    store_name = "Dropshop Electronics"
    sender = {"name": "bright", "email": "brightboadujnr@gmail.com"}

    try:
        order = Order.objects.get(id=order_id)
    except order.DoesNotExist:
        print("Order not found")
        return

    subject = "Thank You for Your Order with Dropshop"

    # Add styled HTML content
    message = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                }}
                .header {{
                    text-align: center;
                    color: #ffffff;
                    background-color: #007bff;
                    padding: 10px;
                    border-radius: 10px 10px 0 0;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    padding: 20px;
                }}
                .order-details {{
                    margin: 20px 0;
                }}
                .order-details th, .order-details td {{
                    text-align: left;
                    padding: 5px 10px;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #555;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Thank You for Your Order</h1>
                </div>
                <div class="content">
                    <p>Hi <b>{order.name}</b>,</p>
                    <p>Thank you for shopping with us! We’re excited to let you know that we’ve received your order and it’s currently being processed. Here are the details of your order:</p>

                    <div class="order-details">
                        <h2>Order Summary</h2>
                        <table>
                            <tr>
                                <th>Order Number:</th>
                                <td>{order.order_number}</td>
                            </tr>
                            <tr>
                                <th>Order Date:</th>
                                <td>{order.created_at.strftime('%Y-%m-%d')}</td>
                            </tr>
                            <tr>
                                <th>Shipping Address:</th>
                                <td>{order.shipping_address}</td>
                            </tr>
                        </table>
                    </div>

                    <h3>Items Ordered:</h3>
                    <ul>
                        {"".join(f"<li>{item.product.name} - {item.quantity} x ${item.price_at_order}</li>" for item in order.items.all())}
                    </ul>

                    <p><strong>Total Amount:</strong> ${order.total_amount:.2f}</p>

                    <h3>What’s Next?</h3>
                    <p>We will notify you once your order is shipped and provide tracking information, so you can follow your order right to your doorstep. In the meantime, if you have any questions, feel free to reach out to our customer service team at {order.phone_number}.</p>

                    <p>Thank you for choosing {store_name}. We hope you enjoy your purchase!</p>
                </div>
                <div class="footer">
                    <p>Warm regards,<br>The {store_name} Team</p>
                </div>
            </div>
        </body>
        </html>
    """

    BREVO_API_KEY = os.getenv("BREVO_API_KEY")

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }

    data = {
        "sender": {"name": sender["name"], "email": sender["email"]},
        "to": [{"email": order.email, "name": order.name}],
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
        order.save()

        send_order_confirmation_mail.delay(order_id)

        return {
            "status": True,
            "message": f"Order {order.order_number} processed successfully",
        }
    except Order.DoesNotExist:
        return {"status": "failed", "message": "Order not found"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
