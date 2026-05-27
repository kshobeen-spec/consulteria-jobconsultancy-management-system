from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
# from .models import UserProfile  # assuming you have a profile model
 
# Admin panel branding
admin.site.site_header = "Consulteria Admin"
admin.site.site_title = "Consulteria Admin Portal"
admin.site.index_title = "Welcome to Consulteria"

# Register UserProfile
# @admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'role')  # replace with your fields
    search_fields = ('user__username', 'phone')
