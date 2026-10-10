from collections import defaultdict
from datetime import date, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from apps.home.models import DailyCheckIn
from apps.nudges.services import ensure_default_templates
from apps.profile.models import Profile
from apps.goals.models import SelfCareGoal
from .models import PodMembership, PodStreak, PodDailySummary, PodMatchingPreference
from .services import get_or_create_user_pod, update_pod_daily_status


def calculate_user_streak(user_dates, today):
    """Calculates the consecutive daily check-in streak from a set of dates in memory."""
    user_checked_in = (today in user_dates)
    check_date = today if user_checked_in else (today - timedelta(days=1))
    streak = 0
    while check_date in user_dates:
        streak += 1
        check_date -= timedelta(days=1)
    return streak, user_checked_in


@login_required
def my_pod_view(request):
    """
    Dedicated view for the user's 5-member micro-pod.
    Displays pod health, member roster cards, shared streak history,
    individual habits, and rhythm preferences.
    """
    today = date.today()
    pod = get_or_create_user_pod(request.user)

    # Ensure daily summary is updated
    update_pod_daily_status(pod, today)

    # Days with pod
    formation_date = pod.formation_date or today
    day_number = max((today - formation_date).days + 1, 1)

    # Active memberships
    memberships = list(
        PodMembership.objects.filter(pod=pod, status='active')
        .select_related('user', 'user__profile')
    )

    member_users = [m.user for m in memberships]
    member_user_ids = [u.id for u in member_users]

    # Batch 1: Fetch recent check-ins for all pod members (last 60 days)
    recent_checkins = list(
        DailyCheckIn.objects.filter(
            user__in=member_users,
            date__gte=today - timedelta(days=60),
            date__lte=today
        ).values_list('user_id', 'date')
    )
    user_checkins_map = defaultdict(set)
    date_checkin_counts = defaultdict(int)
    for u_id, c_date in recent_checkins:
        user_checkins_map[u_id].add(c_date)
        if today - timedelta(days=6) <= c_date <= today:
            date_checkin_counts[c_date] += 1

    # Today's checked in user IDs
    checked_in_user_ids = {u_id for u_id, c_date in recent_checkins if c_date == today}
    total_members = len(memberships) or 5
    checked_in_count = len(checked_in_user_ids)
    progress_pct = int((checked_in_count / total_members) * 100) if total_members else 0

    # Batch 2: Fetch all active habits for all pod members in a single query
    all_goals = list(
        SelfCareGoal.objects.filter(
            user__in=member_users,
            is_active=True
        ).values('user_id', 'title')
    )
    user_goals_map = defaultdict(list)
    for g in all_goals:
        user_goals_map[g['user_id']].append(g['title'])

    # Detailed member roster
    pod_members = []
    for m in memberships:
        member_user = m.user
        member_profile = getattr(member_user, 'profile', None)
        if not member_profile:
            member_profile, _ = Profile.objects.get_or_create(
                user=member_user,
                defaults={'nickname': member_user.username}
            )

        is_self = (member_user.id == request.user.id)
        is_checked = (member_user.id in checked_in_user_ids)
        streak, _ = calculate_user_streak(user_checkins_map[member_user.id], today)

        # Retrieve member goals from in-memory batch
        db_goals = user_goals_map.get(member_user.id, [])
        if not db_goals:
            db_goals = member_profile.goals if isinstance(member_profile.goals, list) else ['Study sprint', 'Hydrate']

        nickname = member_profile.nickname or member_user.username
        initials = nickname[:2].upper() if len(nickname) >= 2 else "AP"

        # Tenure in pod
        joined_date = m.joined_at.date() if m.joined_at else formation_date
        days_in_pod = max((today - joined_date).days + 1, 1)

        pod_members.append({
            'user_id': member_user.id,
            'nickname': nickname,
            'role': 'Pod Anchor' if m.role == 'anchor' else 'Pod Member',
            'status': 'Checked in today' if is_checked else 'Pending check-in',
            'is_checked': is_checked,
            'is_self': is_self,
            'initials': initials,
            'avatar_color': member_profile.avatar_color,
            'profile_image': member_profile.profile_image if member_profile.profile_image else None,
            'bio': member_profile.bio or 'Focusing on small daily habits.',
            'streak': streak,
            'days_in_pod': days_in_pod,
            'joined_display': joined_date.strftime("%b %d, %Y"),
            'goals': db_goals[:3],
        })

    # Keep current user first, then sort by nickname
    pod_members.sort(key=lambda m: (not m['is_self'], m['nickname'].lower()))

    # Pod streak
    streak_obj, _ = PodStreak.objects.get_or_create(
        pod=pod,
        defaults={'current_streak': 0, 'longest_streak': 0}
    )

    # 7-Day Pod Momentum History (Computed in-memory)
    momentum_history = []
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i in range(6, -1, -1):
        hist_date = today - timedelta(days=i)
        hist_checked = date_checkin_counts[hist_date]
        hist_all_completed = (hist_checked == total_members and total_members > 0)
        hist_pct = int((hist_checked / total_members) * 100) if total_members else 0

        momentum_history.append({
            'date': hist_date,
            'day_name': day_labels[hist_date.weekday()],
            'day_display': hist_date.strftime("%b %d"),
            'is_today': (hist_date == today),
            'checked_in_count': hist_checked,
            'total_members': total_members,
            'ratio_str': f"{hist_checked}/{total_members}",
            'all_completed': hist_all_completed,
            'progress_pct': hist_pct,
        })

    # Student matching preference
    preference, _ = PodMatchingPreference.objects.get_or_create(
        user=request.user,
        defaults={'preferred_time_slot': 'Evening', 'timezone': 'Asia/Manila'}
    )

    # Pre-approved nudge templates
    nudge_templates = ensure_default_templates()

    return render(request, "pods/my_pod.html", {
        "pod": pod,
        "day_number": day_number,
        "pod_members": pod_members,
        "checked_in_count": checked_in_count,
        "total_members": total_members,
        "progress_pct": progress_pct,
        "pod_streak": streak_obj,
        "momentum_history": momentum_history,
        "preference": preference,
        "nudge_templates": nudge_templates,
        "today_display": today.strftime("%A, %B %d"),
    })


@login_required
@require_POST
def update_matching_preferences_view(request):
    """Updates user's preferred study time slot and timezone."""
    time_slot = request.POST.get("preferred_time_slot", "Evening").strip()
    timezone = request.POST.get("timezone", "Asia/Manila").strip()

    valid_slots = ["Morning", "Afternoon", "Evening", "Night"]
    if time_slot not in valid_slots:
        time_slot = "Evening"

    preference, _ = PodMatchingPreference.objects.get_or_create(user=request.user)
    preference.preferred_time_slot = time_slot
    preference.timezone = timezone or "Asia/Manila"
    preference.save()

    messages.success(request, f"Your study rhythm has been set to {time_slot} ({preference.timezone}).")
    return redirect("pods:my_pod")
