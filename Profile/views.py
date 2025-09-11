from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Profile
from .serializers import ProfileSerializer
from permissions.custom_permissions import IsOwner

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def perform_create(self, serializer):
        # Assign the logged-in user automatically
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Optional: Return only the profiles of the logged-in user
        return self.queryset.filter(user=self.request.user)
