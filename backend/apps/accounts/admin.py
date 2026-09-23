from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ["username", "email", "role", "is_staff", "is_active"]
    fieldsets = UserAdmin.fieldsets + (
        ("Papel no EducaPortal", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Papel no EducaPortal", {"fields": ("role",)}),
    )
