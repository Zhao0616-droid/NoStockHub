from django.contrib import admin
from .models import User, Role

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role_type', 'is_active', 'is_staff']
    search_fields = ['username', 'email']
    list_filter = ['role_type', 'is_active']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
