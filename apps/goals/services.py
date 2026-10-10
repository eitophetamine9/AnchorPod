from datetime import date
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import SelfCareGoal, DailyGoalCompletion

User = get_user_model()

DEFAULT_GOALS = [
    {
        "title": "Drink a glass of water",
        "category": "physical",
        "sort_order": 1,
    },
    {
        "title": "Step outside or breathe fresh air",
        "category": "mindfulness",
        "sort_order": 2,
    },
    {
        "title": "Study or rest for 25 minutes",
        "category": "academic",
        "sort_order": 3,
    },
]

VALID_CATEGORIES = {
    "physical": "Physical",
    "mindfulness": "Mindfulness",
    "academic": "Academic",
    "wellness": "Wellness",
}


def get_or_create_user_goals(user):
    """
    Returns active SelfCareGoal instances for the user.
    If the user has no goals, automatically seeds the 3 foundational self-care habits.
    """
    goals = list(SelfCareGoal.objects.filter(user=user, is_active=True).order_by('sort_order', 'id'))
    if not goals:
        new_goals = []
        for g_data in DEFAULT_GOALS:
            new_goals.append(
                SelfCareGoal(
                    user=user,
                    title=g_data["title"],
                    category=g_data["category"],
                    sort_order=g_data["sort_order"],
                    is_active=True,
                )
            )
        SelfCareGoal.objects.bulk_create(new_goals)
        goals = list(SelfCareGoal.objects.filter(user=user, is_active=True).order_by('sort_order', 'id'))
    return goals


def get_user_goals_with_today_status(user, target_date=None):
    """
    Returns a list of dictionaries containing each active goal, its category,
    and a boolean indicating whether it was completed for target_date (today).
    """
    if target_date is None:
        target_date = date.today()

    goals = get_or_create_user_goals(user)
    completed_goal_ids = set(
        DailyGoalCompletion.objects.filter(
            user=user,
            date=target_date,
            completed=True
        ).values_list('goal_id', flat=True)
    )

    results = []
    for g in goals:
        results.append({
            "id": g.id,
            "title": g.title,
            "category": g.category,
            "completed": (g.id in completed_goal_ids),
        })

    completed_count = len(completed_goal_ids & {g.id for g in goals})
    total_count = len(goals)

    return results, completed_count, total_count


def toggle_goal_completion(user, goal_id, target_date=None):
    """
    Toggles the completed state for a user's goal on target_date.
    Returns (completion_obj, is_completed, completed_count, total_count, error).
    """
    if target_date is None:
        target_date = date.today()

    goal = SelfCareGoal.objects.filter(id=goal_id, user=user, is_active=True).first()
    if not goal:
        return None, False, 0, 0, "Goal not found."

    with transaction.atomic():
        completion, created = DailyGoalCompletion.objects.get_or_create(
            goal=goal,
            user=user,
            date=target_date,
            defaults={'completed': True}
        )

        if not created:
            completion.completed = not completion.completed
            completion.save()
        is_completed = completion.completed

        # Calculate updated counts
        active_goal_ids = set(SelfCareGoal.objects.filter(user=user, is_active=True).values_list('id', flat=True))
        completed_count = DailyGoalCompletion.objects.filter(
            user=user,
            goal_id__in=active_goal_ids,
            date=target_date,
            completed=True
        ).count()
        total_count = len(active_goal_ids)

    return completion, is_completed, completed_count, total_count, None


def create_custom_goal(user, title, category="wellness"):
    """
    Creates a new custom goal for the user if they haven't exceeded the maximum limit (8).
    """
    title = title.strip()
    if not title:
        return None, "Goal title cannot be empty."

    if len(title) > 120:
        return None, "Goal title cannot exceed 120 characters."

    if category not in VALID_CATEGORIES:
        category = "wellness"

    active_count = SelfCareGoal.objects.filter(user=user, is_active=True).count()
    if active_count >= 8:
        return None, "You can have a maximum of 8 active goals to prevent overwhelm."

    goal = SelfCareGoal.objects.create(
        user=user,
        title=title,
        category=category,
        sort_order=active_count + 1,
        is_active=True,
    )
    return goal, None


def delete_goal(user, goal_id):
    """
    Deactivates a goal owned by the user.
    """
    goal = SelfCareGoal.objects.filter(id=goal_id, user=user).first()
    if not goal:
        return False, "Goal not found."

    goal.is_active = False
    goal.save()
    return True, None
