from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from apps.profile.models import Profile
from apps.user_settings.models import UserSettings


class RegisterVerticalSliceTests(TestCase):
    def test_register_page_renders_cleanly(self):
        response = self.client.get(reverse('register:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register/register.html')
        self.assertContains(response, 'Create your account')

    def test_successful_registration_creates_profile_and_settings(self):
        response = self.client.post(reverse('register:register'), {
            'username': 'newstudent@univ.edu',
            'password': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
        }, follow=True)

        self.assertEqual(response.redirect_chain, [(reverse('login:login'), 302)])
        user = User.objects.get(username='newstudent@univ.edu')
        self.assertIsNotNone(user)
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertTrue(UserSettings.objects.filter(user=user).exists())

    def test_password_mismatch_shows_error(self):
        response = self.client.post(reverse('register:register'), {
            'username': 'student2@univ.edu',
            'password': 'SecurePassword123!',
            'password2': 'DifferentPassword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match.')
