# Create your models here.
# from django.db import models
from django.conf import settings

from django.contrib.auth import get_user_model

User = get_user_model()

from django.db import models

class Booking(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    ai_feedback = models.TextField(blank=True, null=True)
    ai_score = models.FloatField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    service = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} — {self.service} ({self.submitted_at.date()})"

        submitted_at = models.DateTimeField(auto_now_add=True)

    # STATUS (user will see)
    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Rejected", "Rejected"),
            ("Completed", "Completed"),
        ],
        default="Pending"
    )
   

    # ADMIN NOTES (user will see because you said YES)
    admin_notes = models.TextField(null=True, blank=True)
 
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    def __str__(self):
        return self.user.username

from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics/', default='default_profile.png')
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

from django.db import models
from django.conf import settings

class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return self.name

        DUMMY_SERVICES = [
    {"name": "Career Guidance", "staff": "Ayesha Khan", "duration": "30 min"},
    {"name": "Resume Review", "staff": "Rahul Mehta", "duration": "20 min"},
    {"name": "LinkedIn Optimization", "staff": "Sarah Roy", "duration": "40 min"},
]


 

class Payment(models.Model):
    PAYMENT_STATUS = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Failed", "Failed"),
    ]
    booking = models.ForeignKey("Booking", on_delete=models.CASCADE, related_name="payments")
    amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="Pending")
    provider_ref = models.CharField(max_length=200, blank=True, null=True)  # gateway ref
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)


    def __str__(self):
        return f"Payment {self.id} — {self.booking.full_name} — {self.status}"


class Cancellation(models.Model):
    ACTIONS = [
        ("Cancelled", "Cancelled"),
        ("Rescheduled", "Rescheduled"),
    ]
    booking = models.ForeignKey("Booking", on_delete=models.CASCADE, related_name="cancellations")
    action = models.CharField(max_length=20, choices=ACTIONS)
    reason = models.TextField(blank=True, null=True)
    # optional new schedule fields for reschedule
    new_date = models.DateField(null=True, blank=True)
    new_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} — {self.booking.full_name} ({self.created_at.date()})"


class TrainingProgram(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField(default=0)  # in your currency
    sessions = models.IntegerField(default=1)  # number of sessions
    duration = models.CharField(max_length=100, blank=True)  # e.g. "4 weeks"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

