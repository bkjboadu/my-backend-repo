# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
# from django.core.mail import send_mail
# from django.core.mail import get_connection, send_mail
# import os
# import base64
# import jwt
# from django.utils.html import strip_tags
# from django.template.loader import render_to_string
# from django.contrib.sites.shortcuts import get_current_site

# import os
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
# from django.template.loader import render_to_string
# from django.core.mail import EmailMultiAlternatives


# # def send_activation_email(request, user):
# #     token = jwt.encode({'user_id': user.id}, 'secret_key', algorithm='HS256')
# #     current_site = get_current_site(request)
# #     encoded_token = base64.urlsafe_b64encode(token.encode('utf-8')).decode('utf-8')

# #     activation_url = f'http://{current_site.domain}/auth_user/activate/{encoded_token}'
# #     context = {
# #         'user': user,
# #         'activation_url': activation_url
# #     }
# #     message = render_to_string('activate_email.html', context)
# #     plain_message = strip_tags(message)
# #     sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
# #     from_email = os.getenv('EMAIL_HOST_USER')

# #     email = Mail(
# #         from_email=from_email,
# #         to_emails=user.email,
# #         subject='Activate your account',
# #         html_content=message,
# #         plain_text_content=plain_message
# #     )

# #     try:
# #         sg = SendGridAPIClient(sendgrid_api_key)
# #         response = sg.send(email)

# #         if response.status_code == 202:
# #             print("Email sent successfully!")
# #         else:
# #             print(f"Error sending email: Status code {response.status_code}")
# #     except Exception as e:
# #         print(f"Error sending email with SendGrid: {e}")








# from django.core.mail import EmailMultiAlternatives
# from django.utils.html import strip_tags


# def send_activation_email(request, user):
#     token = jwt.encode({'user_id': user.id}, 'secret_key', algorithm='HS256')
#     current_site = get_current_site(request)
#     encoded_token =  base64.urlsafe_b64encode(token.encode('utf-8')).decode('utf-8')

#     activation_url = f'http://{current_site.domain}/auth_user/activate/{encoded_token}'
#     message = render_to_string('activate_email.html', {
#         'user': user,
#         'activation_url': activation_url
#     })
#     plain_message = strip_tags(message)
#     email = EmailMultiAlternatives(
#         'Activate your account',
#         plain_message,
#         os.getenv('EMAIL_HOST_USER'),
#         [user.email],
#     )
#     email.attach_alternative(message, "text/html")
#     email.send()
#     connection = get_connection()
#     connection.open()



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
    token = jwt.encode({'user_id': str(user.id)}, 'secret_key', algorithm='HS256')
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
        os.getenv('EMAIL_HOST_USERS'),
        [user.email],
    )
    email.attach_alternative(message, "text/html")

    email.send()
    connection = get_connection()
    connection.open()
