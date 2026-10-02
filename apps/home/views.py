from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
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
    user_checked_in = DailyCheckIn.objects.filter(user=request.user, date=today).exists()

    user_initials = (profile.nickname[:2].upper() if len(profile.nickname) >= 2 else "ME")

    pod_members = [
        {
            'nickname': profile.nickname,
            'status': 'Checked in' if user_checked_in else 'Not checked in',
            'initials': user_initials,
            'active': user_checked_in,
            'is_self': True,
        },
        {'nickname': 'Northstar', 'status': 'Checked in', 'initials': 'NS', 'active': True, 'is_self': False},
        {'nickname': 'Juniper', 'status': 'Checked in', 'initials': 'JU', 'active': True, 'is_self': False},
        {'nickname': 'Moss', 'status': 'Not checked in', 'initials': 'MO', 'active': False, 'is_self': False},
        {'nickname': 'Solace', 'status': 'Checked in', 'initials': 'SO', 'active': True, 'is_self': False},
    ]

    checked_in_count = sum(1 for m in pod_members if m['active'])
    base_streak = 4
    streak = base_streak + 1 if user_checked_in else base_streak

    return render(request, "home/home.html", {
        "profile": profile,
        "pod_members": pod_members,
        "checked_in": checked_in_count,
        "total_members": len(pod_members),
        "user_checked_in": user_checked_in,
        "streak": streak,
        "today_display": today.strftime("%A, %B %d"),
        "today_chip": today.strftime("%b %d").upper(),
    })


@login_required
def check_in_view(request):
    if request.method == "POST":
        today = date.today()
        DailyCheckIn.objects.get_or_create(user=request.user, date=today)
        messages.success(request, "Your pod can see that you showed up today.")
    return redirect("home:home")


@login_required
def nudge_view(request):
    if request.method == "POST":
        target = request.POST.get("target", "a pod member")
        messages.success(request, f"Anonymous nudge sent to {target}! Small reminders make a big difference.")
    return redirect("home:home")
