from datetime import date, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from apps.nudges.services import ensure_default_templates, get_unread_nudges_for_user
from apps.pods.services import get_or_create_user_pod, update_pod_daily_status
from apps.pods.models import PodMembership
from apps.profile.models import Profile
from .models import DailyCheckIn


@login_required
def home_view(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'nickname': f"Anchor {request.user.username[:1].upper() or 'A'}",
            'goals': ['Drink water', 'Step outside', 'Study for 25 minutes'],
        }
    )

    today = date.today()

    # Retrieve or allocate user's active Pod
    pod = get_or_create_user_pod(request.user)

    # Fetch active memberships and their profiles
    memberships = list(
        PodMembership.objects.filter(pod=pod, status='active')
        .select_related('user', 'user__profile')
    )

    member_users = [m.user for m in memberships]
    checked_in_user_ids = set(
        DailyCheckIn.objects.filter(user__in=member_users, date=today).values_list('user_id', flat=True)
    )

    user_checked_in = request.user.id in checked_in_user_ids

    pod_members = []
    for m in memberships:
        member_user = m.user
        member_profile = getattr(member_user, 'profile', None)
        if not member_profile:
            member_profile, _ = Profile.objects.get_or_create(
                user=member_user,
                defaults={'nickname': member_user.username}
            )

        is_checked = member_user.id in checked_in_user_ids
        is_self = (member_user.id == request.user.id)
        nickname = member_profile.nickname or member_user.username
        initials = nickname[:2].upper() if len(nickname) >= 2 else "AP"

        pod_members.append({
            'user_id': member_user.id,
            'nickname': nickname,
            'status': 'Checked in' if is_checked else 'Not checked in',
            'initials': initials,
            'avatar_color': member_profile.avatar_color,
            'profile_image': member_profile.profile_image if member_profile.profile_image else None,
            'active': is_checked,
            'is_self': is_self,
        })

    # Keep self at the top of the list
    pod_members.sort(key=lambda m: (not m['is_self'], m['nickname'].lower()))

    checked_in_count = len(checked_in_user_ids)
    total_members = len(memberships) or 5

    # Update summary and streak
    update_pod_daily_status(pod, today)

    # Day Counter: Days with Pod
    formation_date = pod.formation_date or today
    day_number = max((today - formation_date).days + 1, 1)

    # Dynamic Consecutive Day Counter (Streak from real user DailyCheckIn records)
    if user_checked_in:
        streak = 1
        check_date = today - timedelta(days=1)
        while DailyCheckIn.objects.filter(user=request.user, date=check_date).exists():
            streak += 1
            check_date -= timedelta(days=1)
    else:
        # Check if user had an active streak through yesterday
        streak = 0
        check_date = today - timedelta(days=1)
        while DailyCheckIn.objects.filter(user=request.user, date=check_date).exists():
            streak += 1
            check_date -= timedelta(days=1)

    # Dynamic Week-at-a-Glance Tracker (Monday to Sunday)
    start_of_week = today - timedelta(days=today.weekday())
    day_labels = ["M", "T", "W", "T", "F", "S", "S"]
    week_days = []
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        is_today = (day_date == today)
        is_past = (day_date < today)
        is_future = (day_date > today)

        user_checked = DailyCheckIn.objects.filter(user=request.user, date=day_date).exists()

        week_days.append({
            "label": day_labels[i],
            "date": day_date,
            "full_date": day_date.strftime("%A, %B %d"),
            "is_today": is_today,
            "is_past": is_past,
            "is_future": is_future,
            "completed": user_checked,
            "user_checked": user_checked,
        })

    progress_pct = int((checked_in_count / total_members) * 100) if total_members else 0

    # Retrieve unread nudges and pre-approved templates
    unread_nudges = get_unread_nudges_for_user(request.user)
    nudge_templates = ensure_default_templates()

    return render(request, "home/home.html", {
        "profile": profile,
        "pod": pod,
        "pod_members": pod_members,
        "checked_in": checked_in_count,
        "total_members": total_members,
        "user_checked_in": user_checked_in,
        "streak": streak,
        "day_number": day_number,
        "week_days": week_days,
        "progress_pct": progress_pct,
        "unread_nudges": unread_nudges,
        "nudge_templates": nudge_templates,
        "today_display": today.strftime("%A, %B %d"),
        "today_chip": today.strftime("%b %d").upper(),
    })


@login_required
def check_in_view(request):
    if request.method == "POST":
        today = date.today()
        DailyCheckIn.objects.get_or_create(user=request.user, date=today)
        pod = get_or_create_user_pod(request.user)
        update_pod_daily_status(pod, today)
        messages.success(request, "Your pod can see that you showed up today.")
    return redirect("home:home")


@login_required
def nudge_view(request):
    if request.method == "POST":
        target = request.POST.get("target", "a pod member")
        messages.success(request, f"Anonymous nudge sent to {target}! Small reminders make a big difference.")
    return redirect("home:home")
