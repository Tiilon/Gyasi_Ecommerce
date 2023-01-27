from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import *


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (_('login'), {'fields': ('username', 'email', 'password')}),
        # (_('Personal Info'), {'fields': ('username',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        # (_('Important Dates'), {'fields': ('created_at',)})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password')
        }),
    )

    list_display = ('username', 'email')

    search_fields = ('email', 'username')
    ordering = ('-created_at',)
