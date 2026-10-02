from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from apps.home.models import DailyCheckIn


class HomeVerticalSliceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='homestudent@univ.edu', password='TestPassword123!')

    def test_anonymous_access_redirects_to_login(self):
        response = self.client.get(reverse('home:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login:login'), response.url)

    def test_authenticated_user_accesses_home(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('home:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/home.html')
        self.assertContains(response, 'Your shared rhythm')

    def test_check_in_creates_daily_record(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('home:check_in'))
        self.assertRedirects(response, reverse('home:home'))
        self.assertTrue(DailyCheckIn.objects.filter(user=self.user).exists())

    def test_authenticated_user_with_avatar_renders_image(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from apps.profile.models import Profile

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04'
            b'\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44'
            b'\x01\x00\x3b'
        )
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.profile_image = SimpleUploadedFile('home_avatar.gif', small_gif, content_type='image/gif')
        profile.save()

        self.client.force_login(self.user)
        response = self.client.get(reverse('home:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'avatar avatar-img')

