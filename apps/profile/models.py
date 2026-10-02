from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150, blank=True)
    nickname = models.CharField(max_length=32, blank=True)
    bio = models.TextField(blank=True)
    avatar_color = models.CharField(max_length=7, default='#f28c5b')
    profile_image = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True
    )
    goals = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profile_profile'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return self.nickname or self.user.username

    def get_display_name(self):
        return self.nickname or self.full_name or self.user.username

