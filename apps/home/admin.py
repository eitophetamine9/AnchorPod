from django.contrib import admin
from .models import DailyCheckIn


@admin.register(DailyCheckIn)
class DailyCheckInAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "completed", "created_at")
    list_filter = ("date", "completed")
