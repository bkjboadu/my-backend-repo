import base64
import os
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.sites.shortcuts import get_current_site
from auth_user.models import CustomUser
from django.urls import reverse
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode
import jwt
from django.template.loader import render_to_string
from django.shortcuts import render
from django.core.mail import get_connection, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags


def send_activation_email(request, user):
    token = jwt.encode({'user_id': user.id}, 'secret_key', algorithm='HS256')
    current_site = get_current_site(request)
    print("hi")
    print(current_site.domain)
    encoded_token =  base64.urlsafe_b64encode(token.encode('utf-8')).decode('utf-8')
    
    # activation_link = reverse('activate', kwargs={'token': token})
    activation_url = f'http://{current_site.domain}/auth_user/activate/{encoded_token}'
    message = render_to_string('activate_email.html', {
        'user': user,
        'activation_url': activation_url
    })

    plain_message = strip_tags(message)

    email = EmailMultiAlternatives(
        'Activate your account',
        plain_message,
        os.getenv('EMAIL_HOST_USER'),
        [user.email],
    )
    email.attach_alternative(message, "text/html")

    email.send()
    connection = get_connection()
    connection.open()  

   

