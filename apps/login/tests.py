from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginVerticalSliceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student@univ.edu', password='TestPassword123!')

    def test_login_page_renders_cleanly(self):
        response = self.client.get(reverse('login:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/login.html')
        self.assertContains(response, 'Member login')

    def test_successful_login_redirects_to_home(self):
        response = self.client.post(reverse('login:login'), {
            'username': 'student@univ.edu',
            'password': 'TestPassword123!',
        })
        self.assertRedirects(response, reverse('home:home'))

    def test_failed_login_shows_error(self):
        response = self.client.post(reverse('login:login'), {
            'username': 'student@univ.edu',
            'password': 'WrongPassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username/email or password.')
