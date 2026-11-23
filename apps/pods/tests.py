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


class MyPodViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='podstudent@univ.edu',
            password='TestPassword123!'
        )

    def test_anonymous_access_redirects_to_login(self):
        from django.urls import reverse
        response = self.client.get(reverse('pods:my_pod'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login:login'), response.url)

    def test_authenticated_access_renders_my_pod(self):
        from django.urls import reverse
        self.client.force_login(self.user)
        response = self.client.get(reverse('pods:my_pod'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pods/my_pod.html')
        self.assertContains(response, 'The Five Anchors')
        self.assertContains(response, 'Pod Journey')
        self.assertContains(response, 'Collective Consistency')

    def test_update_matching_preferences(self):
        from django.urls import reverse
        from apps.pods.models import PodMatchingPreference
        self.client.force_login(self.user)

        response = self.client.post(reverse('pods:preferences'), {
            'preferred_time_slot': 'Morning',
            'timezone': 'America/New_York',
        })
        self.assertRedirects(response, reverse('pods:my_pod'))

        pref = PodMatchingPreference.objects.get(user=self.user)
        self.assertEqual(pref.preferred_time_slot, 'Morning')
        self.assertEqual(pref.timezone, 'America/New_York')

    def test_pod_matching_anonymous_redirects_to_login(self):
        from django.urls import reverse
        response = self.client.get(reverse('pods:match'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login:login'), response.url)

    def test_pod_matching_get_renders_template(self):
        from django.urls import reverse
        self.client.force_login(self.user)
        response = self.client.get(reverse('pods:match'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pods/matching.html')
        self.assertContains(response, 'Find your <em>quiet study rhythm</em>')
        self.assertContains(response, 'Choose your study window')

    def test_pod_matching_post_allocates_pod_and_updates_preferences(self):
        from django.urls import reverse
        from apps.pods.models import PodMatchingPreference, PodMembership
        self.client.force_login(self.user)

        response = self.client.post(reverse('pods:match'), {
            'preferred_time_slot': 'Night',
            'timezone': 'Asia/Manila',
            'goals': ['Drink water', 'Study 25 mins'],
            'pledge_accepted': 'on',
        })
        self.assertRedirects(response, reverse('pods:my_pod'))

        pref = PodMatchingPreference.objects.get(user=self.user)
        self.assertEqual(pref.preferred_time_slot, 'Night')
        self.assertEqual(pref.timezone, 'Asia/Manila')

        active_membership = PodMembership.objects.filter(user=self.user, status='active').first()
        self.assertIsNotNone(active_membership)
        self.assertEqual(active_membership.pod.time_slot, 'Night')

    def test_pod_activity_anonymous_redirects_to_login(self):
        from django.urls import reverse
        response = self.client.get(reverse('pods:activity'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login:login'), response.url)

    def test_pod_activity_authenticated_renders_join_and_subquery(self):
        from django.urls import reverse
        self.client.force_login(self.user)
        response = self.client.get(reverse('pods:activity'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pods/activity.html')
        self.assertContains(response, 'SQL Joins & Subqueries')
        self.assertContains(response, 'Relational Roster (SQL JOIN)')
        self.assertContains(response, 'Daily Check-In Status (SQL SUBQUERY)')
        self.assertIn('join_sql', response.context)
        self.assertIn('subquery_sql', response.context)
        self.assertIn('INNER JOIN', response.context['join_sql'])
        self.assertIn('SELECT', response.context['subquery_sql'])

    def test_pod_activity_subquery_filters_checked_in_members_accurately(self):
        from django.urls import reverse
        from apps.pods.services import get_or_create_user_pod
        from apps.home.models import DailyCheckIn
        from datetime import date
        pod = get_or_create_user_pod(self.user)

        # Mark only self.user as checked in today
        DailyCheckIn.objects.filter(user=self.user, date=date.today()).delete()
        DailyCheckIn.objects.create(user=self.user, date=date.today())

        self.client.force_login(self.user)
        response = self.client.get(reverse('pods:activity'))
        self.assertEqual(response.status_code, 200)

        subquery_users = [m.user for m in response.context['subquery_results']]
        self.assertIn(self.user, subquery_users)

    def test_pod_history_anonymous_redirects_to_login(self):
        from django.urls import reverse
        response = self.client.get(reverse('pods:history'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login:login'), response.url)

    def test_pod_history_authenticated_renders_template(self):
        from django.urls import reverse
        self.client.force_login(self.user)
        response = self.client.get(reverse('pods:history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pods/history.html')
        self.assertContains(response, 'Pod Journey & Reshuffle History')
        self.assertIn('reshuffle_logs', response.context)
        self.assertIn('memberships', response.context)

    def test_run_pod_reshuffle_rotates_inactive_member(self):
        from apps.pods.services import run_pod_reshuffle
        from apps.pods.models import Pod, PodMembership, PodReshuffleLog
        from datetime import date, timedelta
        from django.utils import timezone as django_tz

        pod = Pod.objects.create(name="Reshuffle Test Pod", status="active")
        dormant_user = User.objects.create_user(username="dormant@univ.edu", password="TestPassword123!")
        
        # Joined 5 days ago, no check-ins
        membership = PodMembership.objects.create(
            user=dormant_user,
            pod=pod,
            status="active"
        )
        old_joined = django_tz.now() - timedelta(days=5)
        PodMembership.objects.filter(id=membership.id).update(joined_at=old_joined)

        results = run_pod_reshuffle(days_inactive=3)
        self.assertGreaterEqual(results["rotated_inactive_count"], 1)

        membership.refresh_from_db()
        self.assertEqual(membership.status, "inactive")
        self.assertTrue(PodReshuffleLog.objects.filter(user=dormant_user, old_pod=pod).exists())




