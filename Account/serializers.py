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


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    password = serializers.CharField(min_length=8, write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        # Get the user from the request context
        user = self.context['request'].user
        
        # Check if old password is correct (use check_password for hashed passwords)
        if not user.check_password(data['old_password']):
            raise ValidationError("Current password is incorrect")
            
        if data['password'] != data['password2']:
            raise ValidationError("New passwords do not match")
            
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(
                username=email,
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
