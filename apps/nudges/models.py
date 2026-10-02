from django.conf import settings
from django.db import models


class NudgeTemplate(models.Model):
    message = models.CharField(max_length=160)
    category = models.CharField(max_length=30, default='gentle')

    class Meta:
        db_table = 'nudge_template'
        verbose_name = 'Nudge Template'
        verbose_name_plural = 'Nudge Templates'

    def __str__(self):
        return f"[{self.category}] {self.message}"


class Nudge(models.Model):
    pod = models.ForeignKey('pods.Pod', on_delete=models.CASCADE, related_name='nudges')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_nudges')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_nudges')
    template = models.ForeignKey(NudgeTemplate, on_delete=models.RESTRICT, related_name='used_nudges')
    date = models.DateField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'nudge_nudge'
        verbose_name = 'Nudge'
        verbose_name_plural = 'Nudges'

    def __str__(self):
        return f"Nudge from {self.sender.username} to {self.recipient.username} on {self.date}"
