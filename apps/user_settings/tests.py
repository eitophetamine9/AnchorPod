from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from apps.user_settings.models import UserSettings


class UserSettingsVerticalSliceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='settingsstudent@univ.edu', password='TestPassword123!')

    def test_anonymous_settings_redirects(self):
        response = self.client.get(reverse('user_settings:settings'))
        self.assertEqual(response.status_code, 302)

    def test_settings_view_renders_and_saves(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('user_settings:settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_settings/settings.html')

        # Update settings
        update_response = self.client.post(reverse('user_settings:settings'), {
            'dark_mode': 'on',
            'receive_nudges': 'on',
        }, follow=True)

        self.assertEqual(update_response.status_code, 200)
        settings = UserSettings.objects.get(user=self.user)
        self.assertTrue(settings.dark_mode)
        self.assertFalse(settings.email_notifications) # wasn't in POST, defaults to False
        self.assertTrue(settings.receive_nudges)
