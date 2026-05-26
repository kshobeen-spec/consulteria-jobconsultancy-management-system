from django.db import models

# Create your models here.
from django.db import models
from users.models import CustomUser

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # AI evaluation fields
    score = models.FloatField(blank=True, null=True)  # e.g., AI suitability score
    suggestions = models.TextField(blank=True, null=True)  # AI suggestions

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"
