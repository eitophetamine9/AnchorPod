from django.contrib import admin
from .models import SelfCareGoal, DailyGoalCompletion


@admin.register(SelfCareGoal)
class SelfCareGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'category', 'is_active', 'sort_order', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('user__username', 'title')


@admin.register(DailyGoalCompletion)
class DailyGoalCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal', 'date', 'completed')
    list_filter = ('completed', 'date')
    search_fields = ('user__username', 'goal__title')
