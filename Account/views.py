from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from .models import User, EmailVerification,PasswordReset
from .serializers import (
    UserSerializer,
    RegisterResponseSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    LoginSerializer,
    LoginResponseSerializer
)
import secrets

# Create your views here.

class UserRegistration(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        try:
            serializer= UserSerializer(data=request.data)
            if serializer.is_valid():
                user= serializer.save()
                token = secrets.token_hex(32)
                email_verification_model= EmailVerification.objects.create(user=user, token=token)
                url = f'http://127.0.0.1:8000/api/accounts/verify-email/{token}'

                try:
                    send_mail(
                        "Subject here",
                        f"click on the link to verify your account  {url}",
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                        )
                except Exception as email_error:
                    user.delete()
                    raise email_error
            

        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
                {"detail": "mail sent."},
                status=status.HTTP_200_OK
            )

class VerifyEmailView(APIView):
    def get(self, request, token):
        try:
            verification = EmailVerification.objects.get(token=token)
            
            if verification.is_valid():
                user = verification.user
                user.is_active = True
                user.is_verified = True
                user.save()
                verification.delete()

                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                refresh = str(refresh)

                return Response({
                    'refresh': refresh,
                    'access': access,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }, status=status.HTTP_200_OK)

            else:
                return Response({"detail": "Link expired"}, status=status.HTTP_404_NOT_FOUND)
        
        except EmailVerification.DoesNotExist:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)



class PasswordResetRequestView(APIView):
    """
    Step 1: User submits email to request a reset link or code.
    """
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)

            # Create or replace existing reset token
            reset_obj, created = PasswordReset.objects.update_or_create(
                user=user,
                defaults={
                    'token': uuid.uuid4(),
                }
            )

            # Send email (you can send token OR verification_code)
            reset_link = f"http://127.0.0.1:8000/api/accounts/reset-password-confirm/{reset_obj.token}/"
            message = (
                f"Your password reset code is: {reset_obj.verification_code}\n\n"
                f"Or click the link: {reset_link}"
            )
            send_mail(
                subject="Password Reset Request",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response(
                {"detail": "Password reset instructions sent to your email."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Step 2: User submits token (or code) + new password to reset.
    """
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"detail": "Password has been reset successfully."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response_data = {
            "refresh": str(refresh),
            "access": access_token,
            "user": UserSerializer(user).data
        }

        # Serialize the response properly
        response_serializer = LoginResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)



class LogoutView(APIView):
    
    def post(self, request):
        refresh_token = request.data.get("refresh")
        print( f"refresh_token : {refresh_token}")

        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # blacklist the token
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)