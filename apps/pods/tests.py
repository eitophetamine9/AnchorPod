from django.contrib.auth import get_user_model
from django.test import TestCase
from apps.pods.models import Pod, PodMembership, PodStreak
from apps.pods.services import get_or_create_user_pod, update_pod_daily_status
from apps.home.models import DailyCheckIn

User = get_user_model()


class PodServicesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1@univ.edu',
            password='TestPassword123!'
        )

    def test_get_or_create_user_pod_allocates_pod_with_peers(self):
        pod = get_or_create_user_pod(self.user)
        self.assertIsNotNone(pod)
        self.assertTrue(Pod.objects.filter(id=pod.id).exists())

        # Verify user is member
        membership = PodMembership.objects.filter(user=self.user, pod=pod, status='active').first()
        self.assertIsNotNone(membership)

        # Verify pod has 5 total active members (user + 4 peers)
        total_members = PodMembership.objects.filter(pod=pod, status='active').count()
        self.assertEqual(total_members, 5)

        # Verify streak record exists
        self.assertTrue(PodStreak.objects.filter(pod=pod).exists())

    def test_get_or_create_user_pod_idempotent(self):
        pod1 = get_or_create_user_pod(self.user)
        pod2 = get_or_create_user_pod(self.user)
        self.assertEqual(pod1.id, pod2.id)

    def test_update_pod_daily_status(self):
        pod = get_or_create_user_pod(self.user)
        checked_count, total, all_completed = update_pod_daily_status(pod)
        self.assertGreaterEqual(checked_count, 0)
        self.assertEqual(total, 5)

        # Log check in for remaining members
        for m in PodMembership.objects.filter(pod=pod, status='active'):
            DailyCheckIn.objects.get_or_create(user=m.user)

        checked_count, total, all_completed = update_pod_daily_status(pod)
        self.assertEqual(checked_count, 5)
        self.assertTrue(all_completed)
