from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, get_connection
from django.contrib.sites.shortcuts import get_current_site
import jwt
import base64
import os

def send_password_reset_email(request, user):
    token = jwt.encode({'user_id': user.id}, 'secret_key', algorithm='HS256') 
    current_site = get_current_site(request)
    
    encoded_token = base64.urlsafe_b64encode(token.encode('utf-8')).decode('utf-8')
    
    reset_url = f'http://{current_site.domain}/auth_user/reset_password/{encoded_token}'
    
    message = render_to_string('password_reset_email.html', {
        'user': user,
        'reset_url': reset_url
    })
    plain_message = strip_tags(message)
    
    email = EmailMultiAlternatives(
        'Reset your password',
        plain_message,
        os.getenv('EMAIL_HOST_USER'),
        [user.email],
    )
    email.attach_alternative(message, "text/html")
    
    email.send()
    connection = get_connection()
    connection.open()
    connection.close()
