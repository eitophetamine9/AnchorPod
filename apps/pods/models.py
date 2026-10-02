from django.conf import settings
from django.db import models


class Pod(models.Model):
    STATUS_CHOICES = [
        ('forming', 'Forming'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=64)
    time_slot = models.CharField(max_length=32, default='Anytime')
    max_capacity = models.IntegerField(default=5)
    status = models.CharField(max_length=20, default='forming', choices=STATUS_CHOICES)
    formation_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pod_pod'
        verbose_name = 'Pod'
        verbose_name_plural = 'Pods'

    def __str__(self):
        return self.name


class PodMembership(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('reassigned', 'Reassigned'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pod_memberships'
    )
    pod = models.ForeignKey(
        Pod,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    role = models.CharField(max_length=20, default='member')
    status = models.CharField(max_length=20, default='active', choices=STATUS_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pod_membership'
        verbose_name = 'Pod Membership'
        verbose_name_plural = 'Pod Memberships'

    def __str__(self):
        return f"{self.user.username} in {self.pod.name} ({self.status})"


class PodMatchingPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matching_preference'
    )
    preferred_time_slot = models.CharField(max_length=32, default='Evening')
    timezone = models.CharField(max_length=50, default='Asia/Manila')
    is_seeking_pod = models.BooleanField(default=True)
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pod_matching_preference'
        verbose_name = 'Pod Matching Preference'
        verbose_name_plural = 'Pod Matching Preferences'

    def __str__(self):
        return f"{self.user.username} ({self.preferred_time_slot})"


class PodStreak(models.Model):
    pod = models.OneToOneField(
        Pod,
        on_delete=models.CASCADE,
        related_name='streak'
    )
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_completed_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pod_streak'
        verbose_name = 'Pod Streak'
        verbose_name_plural = 'Pod Streaks'

    def __str__(self):
        return f"{self.pod.name} Streak: {self.current_streak} days"


class PodDailySummary(models.Model):
    pod = models.ForeignKey(
        Pod,
        on_delete=models.CASCADE,
        related_name='daily_summaries'
    )
    date = models.DateField(auto_now_add=True)
    checked_in_count = models.IntegerField(default=0)
    total_members = models.IntegerField(default=5)
    streak_incremented = models.BooleanField(default=False)

    class Meta:
        db_table = 'pod_daily_summary'
        unique_together = ('pod', 'date')
        verbose_name = 'Pod Daily Summary'
        verbose_name_plural = 'Pod Daily Summaries'

    def __str__(self):
        return f"{self.pod.name} on {self.date}: {self.checked_in_count}/{self.total_members}"


class PodReshuffleLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reshuffle_logs'
    )
    old_pod = models.ForeignKey(
        Pod,
        on_delete=models.CASCADE,
        related_name='evacuated_logs'
    )
    new_pod = models.ForeignKey(
        Pod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admitted_logs'
    )
    reason = models.CharField(max_length=50)
    transitioned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pod_reshuffle_log'
        verbose_name = 'Pod Reshuffle Log'
        verbose_name_plural = 'Pod Reshuffle Logs'

    def __str__(self):
        return f"Reshuffle: {self.user.username} from {self.old_pod.name} ({self.reason})"
