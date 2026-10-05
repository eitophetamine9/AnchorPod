from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from apps.pods.models import Pod, PodMembership
from apps.nudges.models import NudgeTemplate, Nudge
from apps.nudges.services import ensure_default_templates, send_anonymous_nudge

User = get_user_model()


class NudgeSystemTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='nudger@univ.edu', password='TestPassword123!')
        self.user2 = User.objects.create_user(username='nudgee@univ.edu', password='TestPassword123!')
        self.outsider = User.objects.create_user(username='outsider@univ.edu', password='TestPassword123!')

        self.pod = Pod.objects.create(name='Test Pod', status='active')
        self.other_pod = Pod.objects.create(name='Other Pod', status='active')

        PodMembership.objects.create(user=self.user1, pod=self.pod, status='active')
        PodMembership.objects.create(user=self.user2, pod=self.pod, status='active')
        PodMembership.objects.create(user=self.outsider, pod=self.other_pod, status='active')

        ensure_default_templates()
        self.template = NudgeTemplate.objects.first()

    def test_ensure_default_templates(self):
        self.assertGreaterEqual(NudgeTemplate.objects.count(), 1)

    def test_send_nudge_within_pod_succeeds(self):
        nudge, error = send_anonymous_nudge(self.user1, self.user2.id, self.template.id)
        self.assertIsNone(error)
        self.assertIsNotNone(nudge)
        self.assertEqual(nudge.recipient, self.user2)
        self.assertEqual(nudge.sender, self.user1)
        self.assertEqual(nudge.pod, self.pod)
        self.assertFalse(nudge.is_read)

    def test_send_nudge_to_self_fails(self):
        nudge, error = send_anonymous_nudge(self.user1, self.user1.id, self.template.id)
        self.assertIsNone(nudge)
        self.assertIn("cannot send a nudge to yourself", error)

    def test_send_nudge_to_outsider_fails(self):
        nudge, error = send_anonymous_nudge(self.user1, self.outsider.id, self.template.id)
        self.assertIsNone(nudge)
        self.assertIn("within your active pod", error)

    def test_send_nudge_view_http(self):
        self.client.force_login(self.user1)
        response = self.client.post(reverse('nudges:send'), {
            'recipient_id': self.user2.id,
            'template_id': self.template.id,
        })
        self.assertRedirects(response, reverse('home:home'))
        self.assertTrue(Nudge.objects.filter(sender=self.user1, recipient=self.user2).exists())

    def test_dismiss_nudge_view(self):
        nudge, _ = send_anonymous_nudge(self.user1, self.user2.id, self.template.id)
        self.client.force_login(self.user2)
        response = self.client.post(reverse('nudges:dismiss', args=[nudge.id]))
        self.assertRedirects(response, reverse('home:home'))
        nudge.refresh_from_db()
        self.assertTrue(nudge.is_read)
