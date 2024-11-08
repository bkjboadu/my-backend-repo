#!/usr/bin/env python3

import stripe

# Set your Stripe secret key (test mode)
stripe.api_key = "sk_test_51QIfVHGKMeRUo53TvuDlslKhc5kItemH6d80DN5guIXnPgYLb6kwvhKy2UYIqWXFg3NzlGXcPyKXnHEIwHVOs1oL00zqokaLv4"

client_secret = "pi_3QIgqzGKMeRUo53T1WR2sOlf_secret_hjEjgaDetUKXcRwvy49suisPw"
payment_intent_id = client_secret.split("_secret_")[0]

try:
    # Confirm the Payment Intent
    payment_intent = stripe.PaymentIntent.confirm(
        payment_intent_id,
        payment_method="pm_card_visa"  # Use a test payment method
    )

    print(f"Payment Intent Status: {payment_intent.status}")

    if payment_intent.status == "succeeded":
        print("Payment was successful.")
    else:
        print("Payment did not succeed.")

except stripe.error.StripeError as e:
    print("Stripe Error:", str(e))
except Exception as e:
    print("Unexpected error:", str(e))
