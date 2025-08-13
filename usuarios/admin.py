from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('rol',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('rol',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'rol')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')

admin.site.register(CustomUser, CustomUserAdmin)
