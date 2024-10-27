import base64,logging
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenRefreshView

import logging, jwt, asyncio, os
from user_management.oauth import GoogleAuthBackend
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from user_management.helpers.permissions import IsAdminOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from user_management.models import CustomUser


from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.http import Http404, JsonResponse
from django.contrib.auth import login
from django.views import View

from rest_framework.exceptions import NotFound
from .tasks import send_mail
from rest_framework_simplejwt.exceptions import TokenError
from backend.settings import GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET

from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import requests

logging.basicConfig(level=logging.INFO)


# Google login view as a RedirectView
class GoogleLoginView(View):
    def get(self, request, *args, **kwargs):

        client_id = GOOGLE_OAUTH_CLIENT_ID
        redirect_uri = settings.LOGIN_REDIRECT_URL
        google_login_url = (
            f"https://accounts.google.com/o/oauth2/auth?"
            f"response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=openid%20email%20profile"
        )
        return redirect(google_login_url)


class GoogleCallbackView(View):
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        if not code:
            return JsonResponse({"error": "Missing authorization code"}, status=400)

        return JsonResponse({"code": code})
        # auth_url = reverse('google_auth_api')
        # redirect_url = f"{auth_url}?code={code}"
        # return redirect(redirect_url)


class GoogleAuthAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        return self.handle_request(request)

    def get(self, request, *args, **kwargs):
        return self.handle_request(request)

    def handle_request(self, request):
        # Check for authorization code in both query params and request data
        code = request.data.get("code") or request.query_params.get("code")
        if not code:
            return Response(
                {"error": "Missing authorization code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Exchange authorization code for access token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": GOOGLE_OAUTH_CLIENT_SECRET,
            # "redirect_uri": settings.LOGIN_REDIRECT_URL,
            "redirect_uri":"http://localhost:8080/accounts/google/login/",
            "grant_type": "authorization_code",
        }

        token_response = requests.post(token_url, data=data)
        token_json = token_response.json()
        access_token = token_json.get("access_token")
        # logging.info(f"{data}")
        # logging.info(f"Redirect URI being sent: {settings.LOGIN_REDIRECT_URL}")
        # logging.info(f"token_json: {token_json}")
        # logging.info(f"access_token: {access_token}")
        if not access_token:
            return Response(
                {"error": "Failed to retrieve token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            idinfo = id_token.verify_oauth2_token(
                token_json["id_token"],
                google_requests.Request(),
                GOOGLE_OAUTH_CLIENT_ID,
            )
        except ValueError:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch user info from Google
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = requests.get(user_info_url, headers=headers)
        user_info = user_info_response.json()

        return Response(user_info, status=status.HTTP_200_OK)


class UserSignupView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        if request.data.get("method") == "google":
            id_token = request.data.get("id_token")
            backend = GoogleAuthBackend()
            user = backend.authenticate(request, id_token=id_token)
            if user:
                return Response({"message": "Logged in with Google successfully."})
            else:
                return Response(
                    {"message": "Failed to log in with Google."}, status=400
                )
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            return Response(
                {
                    "access": response.data.get("access"),
                    "refresh": response.data.get("refresh"),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(response.data, status=response.status_code)


class Activate(APIView):
    permission_classes = ()

    def post(self, request, token):
        try:
            token = base64.urlsafe_b64decode(token).decode("utf-8")
            decoded_token = jwt.decode(token, "secret_key", algorithms=["HS256"])
            user_id = decoded_token["user_id"]
            user = CustomUser.objects.get(id=user_id)
        except (jwt.exceptions.DecodeError, CustomUser.DoesNotExist):
            raise Http404("Invalid activation link")

        if not user.is_verified:
            user.is_verified = True
            user.is_active = True
            user.save()
            return JsonResponse({"detail": "User has been activated"})
        else:
            return JsonResponse({"detail": "User has already been activated"})


class UserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": user_data,
            },
            status=status.HTTP_200_OK,
        )


class UserProfileUpdateView(generics.UpdateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileUpdateSerializer

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class UserLists(generics.ListAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(email=serializer.validated_data["email"])
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(
            reverse("passwordresetconfirm", kwargs={"uidb64": uidb64, "token": token})
        )

        subject = "Password Reset"
        message = (
            f"Hello {user.first_name},\n\n"
            f"We received a request to reset the password for your account. If you made this request, "
            f"please click the link below to reset your password:\n\n"
            f"{reset_url}\n\n"
            f"If you didn't request a password reset, you can safely ignore this email. "
            f"Your password will not be changed unless you click the link above.\n\n"
            f"Thank you,\n"
            f"The Dropshop Team"
        )
        send_mail.delay(subject=subject, message=message, recipient=user)
        return Response(
            {"success": "Email sent  Click the link in your email to continue"},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirm(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uidb64, token):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data["password"]
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):

            if user.check_password(password):
                return Response(
                    {"detail": "password cannot be the same as previous password."}
                )
            user.set_password(password)
            user.save()
            return Response(
                {"detail": "Password successfully reset."}, status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
        )


class PasswordChange(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_password = serializer.validated_data["current_password"]
        user = self.request.user

        if not user.check_password(current_password):
            raise NotFound("You have entered the wrong password, try again.")

        password = serializer.validated_data["password"]
        user.set_password(password)
        user.save()
        return Response(
            {"detail": "Password has been changed."}, status=status.HTTP_200_OK
        )


class DeleteAccount(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAdminUser]
    serializer_class = DeleteAccountSerializer

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(email=serializer.validated_data["email"])
        user.is_active = False
        user.delete()
        return Response({"detail: user deleted"})


class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        print(self.request.user.is_authenticated)
        refresh_token = request.data.get("refresh_token")
        print(refresh_token)
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

        except TokenError:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        except Exception as e:
            return Response(
                {"error": f"{e}: Failed to logout user."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "User has been logged out successfully."},
            status=status.HTTP_200_OK,
        )
