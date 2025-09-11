from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from datetime import datetime, timedelta
from django.utils import timezone
import uuid
import random


# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", 'admin')

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Account must have is_active=True")
        if extra_fields.get("role") != "admin":
            raise ValueError("Superuser always should be role = admin")
        
        return self.create_user(email=email, password=password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'admin'),
        ('customer', 'customer'),
    )
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email_verified = models.BooleanField(default=False)  # Tracks if email is verified
    email_verification_token = models.CharField(max_length=100, blank=True)  # Stores the email verification token
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified= models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_social_user = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    
    # Creates a unique token using UUID
    token = models.CharField()
    
    # When the verification was created
    created_at = models.DateTimeField(auto_now_add=True)
    
    # When the verification link expires
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = datetime.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_valid(self):
        current_time = timezone.now()
        return current_time <= self.expires_at
    

class PasswordReset(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='password_reset')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    verification_code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)
        if not self.verification_code:
            self.verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() <= self.expires_at