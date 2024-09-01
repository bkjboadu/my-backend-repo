from django.shortcuts import render
import base64
import json
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, LoginSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from auth_user.helpers.permissions import IsAdminOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from auth_user.models import CustomUser, CustomUserManager
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.http import Http404,JsonResponse
from rest_framework.exceptions import NotFound
import jwt
from auth_user.helpers.send_mails import send_activation_email
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth import authenticate, login,logout
from rest_framework_simplejwt.exceptions import TokenError


class UserSignupView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
# class ResendActivationLink(generics.GenericAPIView):
#     permission_classes = ()
#     serializer_class = ResendSerializer
#     def post(self,request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         try:
#             user = CustomUser.objects.get(email=serializer.validated_data['email'])
#         except (CustomUser.DoesNotExist):
#             return Response('detail: user does not exist')
#         if user.is_active == True and user.is_verified== True:
#             return Response('detail: user is already verified')
#         else:
#             send_activation_email(request, user)
#             return Response('detail: activation email sent')

class Activate(APIView):
    permission_classes = ()
    def post(self, request, token):
        try:
            token = base64.urlsafe_b64decode(token).decode('utf-8')
            decoded_token = jwt.decode(token, 'secret_key', algorithms=['HS256'])
            # encoded_token = request.GET.get('token')
            
            user_id = decoded_token['user_id']
            user = CustomUser.objects.get(id=user_id)
            print(user)
        except (jwt.exceptions.DecodeError, CustomUser.DoesNotExist):
            raise Http404('Invalid activation link')
        
        if not user.is_verified:
            user.is_verified = True
            user.is_active = True
            user.save()
            return JsonResponse({'detail': 'User has been activated'})
        else:
            return JsonResponse({'detail': 'User has already been activated'})

class UserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        print(user)
        login(request,user)
        # print(self.request.user)
        refresh = RefreshToken.for_user(user)
        # print(request.user.refresh)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class UserLists(generics.ListAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
