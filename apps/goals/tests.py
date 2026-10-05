from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import SelfCareGoal, DailyGoalCompletion
from .services import (
    get_or_create_user_goals,
    get_user_goals_with_today_status,
    toggle_goal_completion,
    create_custom_goal,
    delete_goal,
)

User = get_user_model()


class GoalsVerticalSliceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='habituser@univ.edu', password='TestPassword123!')
        self.other_user = User.objects.create_user(username='otheruser@univ.edu', password='TestPassword123!')

    def test_default_goals_seeded(self):
        goals = get_or_create_user_goals(self.user)
        self.assertEqual(len(goals), 3)
        titles = [g.title for g in goals]
        self.assertIn("Drink a glass of water", titles)
        self.assertIn("Step outside or breathe fresh air", titles)
        self.assertIn("Study or rest for 25 minutes", titles)

    def test_get_user_goals_with_today_status(self):
        goals, completed_count, total_count = get_user_goals_with_today_status(self.user)
        self.assertEqual(total_count, 3)
        self.assertEqual(completed_count, 0)
        for g in goals:
            self.assertFalse(g["completed"])

    def test_toggle_goal_completion(self):
        goals = get_or_create_user_goals(self.user)
        target_goal = goals[0]

        # Toggle to True
        completion, is_completed, comp_count, tot_count, error = toggle_goal_completion(self.user, target_goal.id)
        self.assertIsNone(error)
        self.assertTrue(is_completed)
        self.assertEqual(comp_count, 1)
        self.assertTrue(DailyGoalCompletion.objects.filter(goal=target_goal, user=self.user, completed=True).exists())

        # Toggle back to False
        completion, is_completed, comp_count, tot_count, error = toggle_goal_completion(self.user, target_goal.id)
        self.assertIsNone(error)
        self.assertFalse(is_completed)
        self.assertEqual(comp_count, 0)

    def test_toggle_other_user_goal_unauthorized(self):
        other_goals = get_or_create_user_goals(self.other_user)
        completion, is_completed, comp_count, tot_count, error = toggle_goal_completion(self.user, other_goals[0].id)
        self.assertIsNotNone(error)
        self.assertIn("Goal not found", error)

    def test_create_custom_goal(self):
        goal, error = create_custom_goal(self.user, "Stretch for 5 minutes", "physical")
        self.assertIsNone(error)
        self.assertEqual(goal.title, "Stretch for 5 minutes")
        self.assertEqual(goal.category, "physical")
        self.assertTrue(goal.is_active)

    def test_create_custom_goal_empty_fails(self):
        goal, error = create_custom_goal(self.user, "   ")
        self.assertIsNone(goal)
        self.assertIn("cannot be empty", error)

    def test_delete_goal(self):
        goals = get_or_create_user_goals(self.user)
        target = goals[0]
        success, error = delete_goal(self.user, target.id)
        self.assertTrue(success)
        target.refresh_from_db()
        self.assertFalse(target.is_active)

    def test_toggle_goal_http_view_ajax(self):
        self.client.force_login(self.user)
        goals = get_or_create_user_goals(self.user)
        response = self.client.post(
            reverse('goals:toggle', args=[goals[0].id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['completed'])
        self.assertEqual(data['completed_count'], 1)

    def test_create_goal_http_view_ajax(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('goals:create'),
            {'title': 'Call family', 'category': 'wellness'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['goal']['title'], 'Call family')
