from django.db import models

# Create your models here.
from django.db import models
from users.models import CustomUser

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ConsultationSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    consultant_name = models.CharField(max_length=200)
    scheduled_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.consultant_name} - {self.scheduled_date}"
