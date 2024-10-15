import base64
import os
from typing import Dict
import requests
from django.contrib.sites.shortcuts import get_current_site
import jwt
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from celery import shared_task


@shared_task
def send_mail(subject, message, recipient, sender: Dict = None, data: Dict = None):

    if sender is None:
        sender = {"name": "bright", "email": "brbojr@gmail.com"}

    if not isinstance(recipient, Dict):
        recipient = model_to_dict(recipient)

    BREVO_API_KEY = os.getenv("BREVO_API_KEY")

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }

    data = {
        "sender": {"name": sender["name"], "email": sender["email"]},
        "to": [{"email": recipient["email"], "name": recipient["first_name"]}],
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


User = get_user_model()


@shared_task
def send_activation_email(domain, user_id):
    user = User.objects.get(id=user_id)
    token = jwt.encode({"user_id": str(user.id)}, "secret_key", algorithm="HS256")
    encoded_token = base64.urlsafe_b64encode(token.encode("utf-8")).decode("utf-8")
    activation_url = f"http://{domain}/accounts/activate/{encoded_token}"

    url = "https://api.brevo.com/v3/smtp/email"
    message = (
        f"Hello {user.first_name},\n\n"
        f"Please activate your account by clicking the link below:\n"
        f"{activation_url}\n\n"
        f"If you did not sign up for this account, please disregard this email."
    )

    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }
    data = {
        "sender": {"name": "bright", "email": os.getenv("EMAIL_HOST_USER")},
        "to": [{"email": user.email, "name": user.first_name}],
        "subject": "Activate your account",
        "htmlContent": message,
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email. Status code: {response.status_code}")
        print(f"Response: {response.text}")
