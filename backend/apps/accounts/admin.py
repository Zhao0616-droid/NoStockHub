from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'role_type', 'is_active', 'created_at')
    list_filter = ('role_type', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'last_login')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('基本信息', {'fields': ('email', 'phone', 'avatar')}),
        ('权限与角色', {'fields': ('role', 'role_type', 'two_factor_enabled')}),
        ('权限控制', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('时间信息', {'fields': ('created_at', 'updated_at', 'last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )