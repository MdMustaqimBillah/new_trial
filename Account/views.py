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
    PasswordChangeSerializer,
    LoginSerializer,
    LoginResponseSerializer
)
import secrets
import uuid


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




class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"detail": "Password has been changed successfully."},
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
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get("refresh") or request.POST.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

        # Clean the token (remove any whitespace/newlines)
        clean_token = refresh_token.strip().replace('\n', '').replace('\r', '').replace(' ', '')
        print(f"Cleaned token: {clean_token}")

        try:
            # token = RefreshToken(clean_token)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_204_NO_CONTENT)
        except TokenError as e:
            print(f"TokenError details: {e}")
            return Response({
                "error": f"Invalid refresh token: {str(e)}",
                "received_token_preview": clean_token[:50] + "..." if len(clean_token) > 50 else clean_token
            }, status=status.HTTP_400_BAD_REQUEST)