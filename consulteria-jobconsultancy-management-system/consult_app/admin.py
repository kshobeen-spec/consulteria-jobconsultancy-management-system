from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "service", "date", "ai_score", "submitted_at")
    list_filter = ("service", "date", "submitted_at")
    search_fields = ("full_name", "email", "service")

fields = (
        "full_name", "email", "phone",
        "service", "date", "time",
        "resume", "ai_score", "ai_feedback",
        "status", "admin_notes"
    )
from .models import UserProfile
admin.site.register(UserProfile)

from .models import Payment
from .models import Cancellation
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "amount", "status", "created_at")
    list_filter = ("status",)

@admin.register(Cancellation)
class CancellationAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "action", "new_date", "new_time", "created_at")
    list_filter = ("action",)

from .models import TrainingProgram
@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "price", "sessions", "created_at")




