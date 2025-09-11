from django.db import models
from Account.models import User

# Create your models here.
class Profile(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile')
    dob = models.DateField(blank=True, null=True)
    full_name= models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.full_name)