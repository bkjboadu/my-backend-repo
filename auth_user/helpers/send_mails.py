from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.core.mail import send_mail
from django.core.mail import get_connection, send_mail

import os
import base64
import jwt
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

def send_activation_email(request, user):

    token = jwt.encode({'user_id': user.id}, 'secret_key', algorithm='HS256')
    encoded_token = base64.urlsafe_b64encode(token.encode('utf-8')).decode('utf-8')
    current_site = get_current_site(request)
    activation_url = f'http://{current_site.domain}/auth_user/activate/{encoded_token}'
    
    message = render_to_string('activate_email.html', {
        'user': user,
        'activation_url': activation_url
    })
    plain_message = strip_tags(message)
    
    email = Mail(
        from_email=os.getenv('EMAIL_HOST_USER'),
        to_emails=user.email,
        subject='Activate your account',
        html_content=message,
        plain_text_content=plain_message
    )
    email.send()
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(email)
        print(f"Activation email sent successfully! Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error sending activation email: {e}")
