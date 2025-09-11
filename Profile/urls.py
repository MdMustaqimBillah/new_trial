from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProfileViewSet

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'profile',ProfileViewSet, basename='profile')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]