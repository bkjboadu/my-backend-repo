import requests
from django.conf import settings

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY

headers = {
    "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    "Content-Type": "application/json",
}

def initialize_transaction(email, amount):
    url = 'https://api.paystack.co/transaction/initialize'
    data = {
        "email": email,
        "amount": amount * 100,
        "payment_channel": ["mobile_money"] ,
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def verify_payment(reference):
    url = f'https://api.paystack.co/transaction/verify/{reference}'
    response = requests.get(url, headers=headers)
    return response.json()
