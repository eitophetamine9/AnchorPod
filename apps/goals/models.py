from django.conf import settings
from django.db import models


class SelfCareGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='selfcare_goals')
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
    goal = models.ForeignKey(SelfCareGoal, on_delete=models.CASCADE, related_name='completions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goal_completions')
    date = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    class Meta:
        db_table = 'goal_dailycompletion'
        unique_together = ('goal', 'user', 'date')
        verbose_name = 'Daily Goal Completion'
        verbose_name_plural = 'Daily Goal Completions'

    def __str__(self):
        return f"{self.user.username} - {self.goal.title} ({self.date}): {'Done' if self.completed else 'Pending'}"
