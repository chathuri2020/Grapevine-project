from io import BytesIO
from django.contrib.auth.models import AbstractUser
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from PIL import Image
import sys


class MyUser(AbstractUser):
    """ User Model with Abstract User"""
    city = models.CharField(max_length=255)
    user_type = models.CharField(max_length=255, choices=(('admin', 'Admin'),
                                                          ('customer', 'Customer')))

    def __str__(self):
        return self.username


class Profile(models.Model):
    """ Profile Model with Profile Image"""
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"{self.user.username}'s Profile"

    
