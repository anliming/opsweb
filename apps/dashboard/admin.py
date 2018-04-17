# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name_cn', 'email', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('name_cn','username')
    list_per_page = 10

