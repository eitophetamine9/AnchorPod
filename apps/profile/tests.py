from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from apps.profile.models import Profile


class ProfileVerticalSliceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='profilestudent@univ.edu', password='TestPassword123!')

    def test_anonymous_profile_redirects(self):
        response = self.client.get(reverse('profile:profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_view_renders_and_updates(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/profile.html')

        # Update profile
        update_response = self.client.post(reverse('profile:profile'), {
            'nickname': 'Anchor Phoenix',
            'full_name': 'Jane Doe',
            'bio': 'Taking it one day at a time.',
            'avatar_color': '#5b8c6a',
            'goals': 'Meditate\nWalk outside\nRead 10 pages',
        }, follow=True)

        self.assertEqual(update_response.status_code, 200)
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.nickname, 'Anchor Phoenix')
        self.assertEqual(profile.avatar_color, '#5b8c6a')
        self.assertIn('Meditate', profile.goals)

    def test_profile_image_upload_and_removal(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.force_login(self.user)

        # 1x1 transparent GIF
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04'
            b'\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44'
            b'\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile('avatar.gif', small_gif, content_type='image/gif')

        response = self.client.post(reverse('profile:profile'), {
            'nickname': 'Anchor Phoenix',
            'profile_image': uploaded,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        profile = Profile.objects.get(user=self.user)
        self.assertTrue(bool(profile.profile_image))
        self.assertIn('avatar', profile.profile_image.name)

        # Verify it renders in the HTML response
        self.assertContains(response, 'data-original-src')

        # Test removing the image
        remove_response = self.client.post(reverse('profile:profile'), {
            'nickname': 'Anchor Phoenix',
            'remove_image': 'on',
        }, follow=True)

        self.assertEqual(remove_response.status_code, 200)
        profile.refresh_from_db()
        self.assertFalse(bool(profile.profile_image))

    def test_large_image_auto_downscaled(self):
        import io
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.force_login(self.user)

        # Create an 800x600 large test image
        large_im = Image.new('RGB', (800, 600), color=(239, 131, 96))
        buf = io.BytesIO()
        large_im.save(buf, format='JPEG')
        buf.seek(0)

        uploaded = SimpleUploadedFile('giant_photo.jpg', buf.getvalue(), content_type='image/jpeg')

        response = self.client.post(reverse('profile:profile'), {
            'nickname': 'Anchor Giant',
            'profile_image': uploaded,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        profile = Profile.objects.get(user=self.user)
        self.assertTrue(bool(profile.profile_image))

        # Check that Pillow auto-cropped to square and downscaled to 400x400 max
        saved_img = Image.open(profile.profile_image.path)
        self.assertEqual(saved_img.size, (400, 400))


