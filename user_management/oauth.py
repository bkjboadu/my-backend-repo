import uuid
from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests
from .models import CustomUser


class GoogleAuthBackend(ModelBackend):
    def authenticate(self, request, google_id_token=None):
        """
        Authenticate a user via Google OAuth2 token.
        """
        if google_id_token is None:
            return None

        try:
            # Verify the token with Google
            id_info = id_token.verify_oauth2_token(
                google_id_token, requests.Request(), settings.GOOGLE_CLIENT_ID
            )

            # Check if the email is valid
            email = id_info.get("email")
            if not email:
                return None

            # Retrieve or create the user
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                user = CustomUser.objects.create_user(
                    email=email,
                    first_name=id_info.get("given_name", ""),
                    last_name=id_info.get("family_name", ""),
                )

            return user

        except ValueError:
            # Token verification failed
            return None

    def get_user(self, user_id):
        """
        Retrieve a user by their primary key.
        """
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
