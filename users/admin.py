from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User  # Импортируйте вашу модель User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff')  # Настройте отображаемые поля
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'city', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
    ordering = ('email',)