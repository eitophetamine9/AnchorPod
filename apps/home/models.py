from django.conf import settings
from django.db import models


class DailyCheckIn(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='checkins')
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

