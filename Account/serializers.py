from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User, EmailVerification, PasswordReset
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RegisterResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()


# --- 🔑 Password Reset Serializers ---
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise ValidationError("User with this email does not exist")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=8, write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise ValidationError("Passwords do not match")
        return data

    def save(self, **kwargs):
        token = self.validated_data['token']
        password = self.validated_data['password']

        try:
            reset_obj = PasswordReset.objects.get(token=token)
        except PasswordReset.DoesNotExist:
            raise ValidationError("Invalid or expired token")

        user = reset_obj.user
        user.set_password(password)
        user.save()

        # Once used, delete token so it cannot be reused
        reset_obj.delete()

        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(
                email=email,
                password=password
            )
            if not user:
                raise ValidationError("Invalid username or password")
        else:
            raise ValidationError("Both username and password are required")

        data['user'] = user
        return data


class LoginResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    user = UserSerializer()
