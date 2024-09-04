# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
# from django.core.mail import EmailMultiAlternatives, get_connection
# from django.contrib.sites.shortcuts import get_current_site
# import jwt
# import base64
# import os

# def send_password_reset_email(request, user):
#     token = jwt.encode({'user_id': user.id}, 'secret_key', algorithm='HS256') 
#     current_site = get_current_site(request)
    
#     encoded_token = base64.urlsafe_b64encode(token.encode('utf-8')).decode('utf-8')
    
#     reset_url = f'http://{current_site.domain}/auth_user/reset_password/{encoded_token}'
    
#     message = render_to_string('password_reset_email.html', {
#         'user': user,
#         'reset_url': reset_url
#     })
#     plain_message = strip_tags(message)
    
#     email = EmailMultiAlternatives(
#         'Reset your password',
#         plain_message,
#         os.getenv('EMAIL_HOST_USER'),
#         [user.email],
#     )
#     email.attach_alternative(message, "text/html")
    
#     email.send()
#     connection = get_connection()
#     connection.open()
#     connection.close()


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
    reset_url = f'http://{current_site.domain}/auth_user/password_reset/{encoded_token}'
    
    message = render_to_string('password_reset_email.html', {
        'user': user,
        'reset_url': reset_url
    })
    plain_message = strip_tags(message)
    
    email = Mail(
        from_email=os.getenv('EMAIL_HOST_USERS'),
        to_emails=user.email,
        subject='Password reset request ',
        html_content=message,
        plain_text_content=plain_message
    )
    email.send()
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(email)
        print(f"Password reset mail sent successfully! Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error sending activation email: {e}")
