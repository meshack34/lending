from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # show role in admin list
    list_display = ("username", "email", "role", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )

