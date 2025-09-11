from django.urls import path
from .views import UserRegistration, VerifyEmailView,LoginView, PasswordResetRequestView,PasswordResetConfirmView,LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns=[
    path('register/',UserRegistration.as_view()),
    path('verify-email/<str:token>/',VerifyEmailView.as_view()),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/',LogoutView.as_view()),
    path('password-reset/',PasswordResetRequestView.as_view()),
    path('password-reset-request/',PasswordResetConfirmView.as_view()),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]