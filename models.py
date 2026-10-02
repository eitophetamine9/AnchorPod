"""
AnchorPod - Consolidated Django Models
======================================
This file maps the complete approved Physical Entity-Relationship Diagram (ERD)
for AnchorPod into Django models, covering both the active features and the
planned extensions (Pod Matching Engine, Anonymous Nudges, Daily Habit Logs,
Collective Streaks, and Reshuffling).

CSIT327: Django Vertical Slicing + Supabase Integration
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


# ==============================================================================
# 1. PROFILE & IDENTITY FEATURE (apps.profile)
# ==============================================================================

class Profile(models.Model):
    """
    Extends the Django User (auth_user) with anonymous display handle,
    avatar color/image, bio, and daily self-care goals checklist.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="One-to-one relationship with auth_user."
    )
    full_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="Private full name (never shared with pod peers)."
    )
    nickname = models.CharField(
        max_length=32,
        blank=True,
        help_text="Anonymous pseudonym visible to pod peers."
    )
    bio = models.TextField(
        blank=True,
        help_text="Personal anchor reflection / reminder."
    )
    avatar_color = models.CharField(
        max_length=7,
        default='#ef8360',
        help_text="Hex color code for anonymous avatar."
    )
    profile_image = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True,
        help_text="Cropped profile photo (PNG, JPG, WEBP)."
    )
    goals = models.JSONField(
        default=list,
        blank=True,
        help_text="Quick checklist array of daily goals."
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profile_profile'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return self.nickname or self.user.username

    def get_display_name(self):
        return self.nickname or self.full_name or self.user.username


# ==============================================================================
# 2. USER SETTINGS FEATURE (apps.user_settings)
# ==============================================================================

class UserSettings(models.Model):
    """
    Stores user application preferences including theme and notification toggles.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='settings',
        help_text="One-to-one relationship with auth_user."
    )
    dark_mode = models.BooleanField(
        default=False,
        help_text="Enables dark theme across application."
    )
    email_notifications = models.BooleanField(
        default=True,
        help_text="Enables daily reminder email digests."
    )
    receive_nudges = models.BooleanField(
        default=True,
        help_text="Enables receiving anonymous positive peer nudges."
    )

    class Meta:
        db_table = 'user_settings_usersettings'
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'

    def __str__(self):
        return f"Settings for {self.user.username}"


# ==============================================================================
# 3. DAILY CHECK-IN FEATURE (apps.home)
# ==============================================================================

class DailyCheckIn(models.Model):
    """
    Records daily attendance when a student clicks 'Check in with my pod'.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='checkins'
    )
    date = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'home_dailycheckin'
        unique_together = ('user', 'date')
        verbose_name = 'Daily Check-In'
        verbose_name_plural = 'Daily Check-Ins'

    def __str__(self):
        return f"{self.user.username} - {self.date}"


# ==============================================================================
# 4. PODS & MATCHING ENGINE (apps.pods)
# ==============================================================================

class Pod(models.Model):
    """
    The 5-student anonymous accountability unit.
    """
    STATUS_CHOICES = [
        ('forming', 'Forming'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=64, help_text="e.g. 'Pod 07', 'Solace Pod'")
    time_slot = models.CharField(max_length=32, default='Anytime', help_text="e.g. 'Morning', 'Evening'")
    max_capacity = models.IntegerField(default=5, help_text="Fixed at 5 per project spec.")
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
    """
    Associative table resolving the Many-to-Many relationship between User and Pod,
    preserving historical assignments and current membership status.
    """
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
    """
    User availability criteria used by the Python matching engine to group students.
    """
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
    """
    Tracks and caches the collective consecutive-day check-in streak of a pod.
    """
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
    """
    Aggregates day-by-day attendance for the dashboard progress ring (e.g. 3/5).
    """
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
    """
    Audit table logging when inactive members are rotated out or dead pods are merged.
    """
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


# ==============================================================================
# 5. GRANULAR SELF-CARE HABITS & GOALS (apps.goals)
# ==============================================================================

class SelfCareGoal(models.Model):
    """
    Individual self-care habit or task defined by a student.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='selfcare_goals'
    )
    title = models.CharField(max_length=120)
    category = models.CharField(max_length=30, default='physical')
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'goal_selfcaregoal'
        verbose_name = 'Self-Care Goal'
        verbose_name_plural = 'Self-Care Goals'

    def __str__(self):
        return f"{self.user.username}: {self.title}"


class DailyGoalCompletion(models.Model):
    """
    Daily completion log for each individual self-care goal.
    """
    goal = models.ForeignKey(
        SelfCareGoal,
        on_delete=models.CASCADE,
        related_name='completions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goal_completions'
    )
    date = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    class Meta:
        db_table = 'goal_dailycompletion'
        unique_together = ('goal', 'user', 'date')
        verbose_name = 'Daily Goal Completion'
        verbose_name_plural = 'Daily Goal Completions'

    def __str__(self):
        return f"{self.user.username} - {self.goal.title} ({self.date}): {'Done' if self.completed else 'Pending'}"


# ==============================================================================
# 6. ANONYMOUS NUDGE SYSTEM (apps.nudges)
# ==============================================================================

class NudgeTemplate(models.Model):
    """
    Pre-approved, positive encouragement phrases to prevent free-text cyberbullying.
    """
    message = models.CharField(max_length=160)
    category = models.CharField(max_length=30, default='gentle')

    class Meta:
        db_table = 'nudge_template'
        verbose_name = 'Nudge Template'
        verbose_name_plural = 'Nudge Templates'

    def __str__(self):
        return f"[{self.category}] {self.message}"


class Nudge(models.Model):
    """
    Record of an anonymous encouragement notification sent from one peer to another.
    """
    pod = models.ForeignKey(
        Pod,
        on_delete=models.CASCADE,
        related_name='nudges'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_nudges'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_nudges'
    )
    template = models.ForeignKey(
        NudgeTemplate,
        on_delete=models.RESTRICT,
        related_name='used_nudges'
    )
    date = models.DateField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'nudge_nudge'
        verbose_name = 'Nudge'
        verbose_name_plural = 'Nudges'

    def __str__(self):
        return f"Nudge from {self.sender.username} to {self.recipient.username} on {self.date}"
