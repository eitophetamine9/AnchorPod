from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "nickname", "full_name", "avatar_color")
    search_fields = ("user__username", "nickname", "full_name")
