from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # extra fields if needed
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username


