from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')  # Read-only, automatically set

    class Meta:
        model = Profile
        fields = ['id', 'full_name', 'dob', 'user']
