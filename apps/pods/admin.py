from django.contrib import admin
from .models import (
    Pod,
    PodMembership,
    PodMatchingPreference,
    PodStreak,
    PodDailySummary,
    PodReshuffleLog,
)


class PodMembershipInline(admin.TabularInline):
    model = PodMembership
    extra = 0


@admin.register(Pod)
class PodAdmin(admin.ModelAdmin):
    list_display = ('name', 'time_slot', 'status', 'max_capacity', 'formation_date', 'created_at')
    list_filter = ('status', 'time_slot')
    search_fields = ('name',)
    inlines = [PodMembershipInline]


@admin.register(PodMembership)
class PodMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'pod', 'role', 'status', 'joined_at')
    list_filter = ('status', 'role', 'pod')
    search_fields = ('user__username', 'pod__name')


@admin.register(PodMatchingPreference)
class PodMatchingPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_time_slot', 'timezone', 'is_seeking_pod', 'requested_at')
    list_filter = ('is_seeking_pod', 'preferred_time_slot')
    search_fields = ('user__username',)


@admin.register(PodStreak)
class PodStreakAdmin(admin.ModelAdmin):
    list_display = ('pod', 'current_streak', 'longest_streak', 'last_completed_date', 'updated_at')


@admin.register(PodDailySummary)
class PodDailySummaryAdmin(admin.ModelAdmin):
    list_display = ('pod', 'date', 'checked_in_count', 'total_members', 'streak_incremented')
    list_filter = ('date', 'streak_incremented')


@admin.register(PodReshuffleLog)
class PodReshuffleLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'old_pod', 'new_pod', 'reason', 'transitioned_at')
    search_fields = ('user__username', 'reason')
