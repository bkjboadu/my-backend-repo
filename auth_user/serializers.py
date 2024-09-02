from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser
from auth_user.helpers.validator import CustomPasswordValidator
from django.core.mail import send_mail

from django.utils.crypto import get_random_string
from auth_user.helpers.send_mails import send_activation_email
import jwt
from django.contrib.auth.hashers import check_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id','email', 'first_name', 'last_name','password')
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate_password(self, password):
        validator = CustomPasswordValidator()
        validator.validate(password)
        return password

    def create(self, validated_data):
        user = CustomUser.objects.create_user(is_active = False,**validated_data)
        
        # token = get_random_string(length=32)
        # token = jwt.encode({'user_id': user.id}, 'token', algorithm='HS256')
        # send an activation email with the activation token
        send_activation_email(request=self.context.get('request'), user=user)
        return user
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = CustomUser.objects.get(email=email)
        if not user:
                raise serializers.ValidationError('Invalid email')
        if password:
            if not check_password(password, user.password):
                raise serializers.ValidationError('Invalid password')
        else:
            raise serializers.ValidationError('Email and password are required')

        data['user'] = user
        return data
    

#Password management
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, data):
        user = CustomUser.objects.filter(email=data).first()
        if not user:
            raise serializers.ValidationError("No account is associated with this email.")
        return data

class PasswordResetConfirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("password","confirm_password")
    confirm_password = serializers.CharField(
        write_only=True,
        required=True
    )

    def validate_password(self, password):
        validator = CustomPasswordValidator()
        validator.validate(password)
        return password
    
    def validate(self, data):
        password = data['password']
        """
        Check that the two password fields match
        """
        if password != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
class PasswordChangeSerializer(PasswordResetConfirmSerializer):
    current_password = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta(PasswordResetConfirmSerializer.Meta):
        fields = ('current_password', 'password', 'confirm_password')
    def password_check(self,data):
        user = self.context['request'].user
        current_password = data['current_password']
        if not user.check_password(current_password):
            raise serializers.ValidationError('you have entered the wrong password check and try again.')
        
    
class DeleteAccountSerializer(PasswordResetSerializer):
    def get_user(self,email):
        user = CustomUser.objects.get(email=email)
        return user