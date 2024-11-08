#!/usr/bin/env python3

import stripe

# Set your Stripe secret key (test mode)
stripe.api_key = "sk_test_51QIfVHGKMeRUo53TvuDlslKhc5kItemH6d80DN5guIXnPgYLb6kwvhKy2UYIqWXFg3NzlGXcPyKXnHEIwHVOs1oL00zqokaLv4"


try:
    # Create a Payment Intent with automatic payment methods enabled
    payment_intent = stripe.PaymentIntent.create(
        amount=5000,  # Amount in cents (i.e., $50.00)
        currency="usd",
        payment_method="pm_card_visa",  # Use a test payment method
        automatic_payment_methods={
            "enabled": True,
            "allow_redirects": "never"
        }
    )

    print(f"Payment Intent Status: {payment_intent.status}")
    print(f"Client Secret: {payment_intent.client_secret}")

except stripe.error.StripeError as e:
    print("Stripe Error:", str(e))
except Exception as e:
    print("Unexpected error:", str(e))
