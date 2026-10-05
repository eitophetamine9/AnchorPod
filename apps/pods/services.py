from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q
from apps.home.models import DailyCheckIn
from apps.profile.models import Profile
from .models import Pod, PodMembership, PodStreak, PodDailySummary

User = get_user_model()

POD_NAMES = [
    "Pod Solace",
    "Pod Aurora",
    "Pod Harbor",
    "Pod Haven",
    "Pod Oasis",
    "Pod Zenith",
    "Pod Beacon",
    "Pod Summit",
]

DEMO_PEERS = [
    {
        "username": "peer_northstar",
        "email": "northstar@university.edu",
        "nickname": "Northstar",
        "avatar_color": "#e07a5f",
        "bio": "Taking it one day at a time.",
        "goals": ["Drink 2L water", "Walk for 15 mins", "Read 10 pages"],
        "checked_in_today": True,
    },
    {
        "username": "peer_juniper",
        "email": "juniper@university.edu",
        "nickname": "Juniper",
        "avatar_color": "#3d405b",
        "bio": "Senior year student trying to stay balanced.",
        "goals": ["Stretch in the morning", "Eat a proper lunch", "Sleep before midnight"],
        "checked_in_today": True,
    },
    {
        "username": "peer_moss",
        "email": "moss@university.edu",
        "nickname": "Moss",
        "avatar_color": "#81b29a",
        "bio": "Stressed about midterms, focusing on small habits.",
        "goals": ["Step outside for fresh air", "10-minute meditation", "Stay hydrated"],
        "checked_in_today": False,
    },
    {
        "username": "peer_solace",
        "email": "solace@university.edu",
        "nickname": "Solace",
        "avatar_color": "#f2cc8f",
        "bio": "Holding rhythm together.",
        "goals": ["Write down 3 gratitudes", "Screen break every hour", "Gentle evening stroll"],
        "checked_in_today": False,
    },
]


def get_or_create_user_pod(user):
    """
    Retrieves the user's active Pod. If none exists, assigns the user
    to an available forming/active Pod with space (<5 members), or creates
    a new Pod and provisions peer members.
    """
    membership = PodMembership.objects.filter(
        user=user,
        status='active'
    ).select_related('pod').first()

    if membership:
        pod = membership.pod
        # Ensure streak object exists
        PodStreak.objects.get_or_create(pod=pod, defaults={'current_streak': 0, 'longest_streak': 0})
        return pod

    with transaction.atomic():
        # Look for open pods with space
        open_pod = (
            Pod.objects.filter(status__in=['forming', 'active'])
            .annotate(active_count=Count('memberships', filter=Q(memberships__status='active')))
            .filter(active_count__lt=5)
            .first()
        )

        if not open_pod:
            # Pick a unique pod name
            existing_count = Pod.objects.count()
            name_idx = existing_count % len(POD_NAMES)
            pod_name = f"{POD_NAMES[name_idx]} {existing_count // len(POD_NAMES) + 1 if existing_count >= len(POD_NAMES) else ''}".strip()
            
            open_pod = Pod.objects.create(
                name=pod_name,
                time_slot="Evening",
                max_capacity=5,
                status='active',
                formation_date=date.today(),
            )

        # Ensure streak record
        PodStreak.objects.get_or_create(
            pod=open_pod,
            defaults={'current_streak': 0, 'longest_streak': 0}
        )

        # Create user's membership
        PodMembership.objects.create(
            user=user,
            pod=open_pod,
            role='member',
            status='active'
        )

        # Ensure pod has peers
        ensure_pod_peers(open_pod, user)

    return open_pod


def ensure_pod_peers(pod, current_user):
    """
    Fills empty slots in a pod with simulated student peers so solo
    developers and new students immediately have an active 5-person community.
    """
    current_members_count = PodMembership.objects.filter(pod=pod, status='active').count()
    if current_members_count >= 5:
        return

    today = date.today()

    for peer_data in DEMO_PEERS:
        if PodMembership.objects.filter(pod=pod, status='active').count() >= 5:
            break

        peer_username = f"{peer_data['username']}_{pod.id}" if Pod.objects.count() > 1 else peer_data['username']
        peer_user, _ = User.objects.get_or_create(
            username=peer_username,
            defaults={'email': f"{peer_username}@university.edu"}
        )

        Profile.objects.get_or_create(
            user=peer_user,
            defaults={
                'nickname': peer_data['nickname'],
                'avatar_color': peer_data['avatar_color'],
                'bio': peer_data['bio'],
                'goals': peer_data['goals'],
            }
        )

        # Link to pod if not already
        membership, created = PodMembership.objects.get_or_create(
            user=peer_user,
            pod=pod,
            defaults={'role': 'member', 'status': 'active'}
        )

        # Simulate check-in for realistic initial UI state
        if peer_data['checked_in_today']:
            DailyCheckIn.objects.get_or_create(user=peer_user, date=today)


def update_pod_daily_status(pod, target_date=None):
    """
    Evaluates check-in completion across all active pod members for target_date.
    Updates or creates PodDailySummary and recalculates PodStreak.
    """
    if target_date is None:
        target_date = date.today()

    active_memberships = list(PodMembership.objects.filter(pod=pod, status='active').select_related('user'))
    total_members = len(active_memberships)
    if total_members == 0:
        return 0, 0, False

    member_users = [m.user for m in active_memberships]
    checked_in_count = DailyCheckIn.objects.filter(
        user__in=member_users,
        date=target_date
    ).count()

    all_completed = (checked_in_count == total_members)

    streak_obj, _ = PodStreak.objects.get_or_create(
        pod=pod,
        defaults={'current_streak': 0, 'longest_streak': 0}
    )

    summary, created = PodDailySummary.objects.get_or_create(
        pod=pod,
        date=target_date,
        defaults={
            'checked_in_count': checked_in_count,
            'total_members': total_members,
            'streak_incremented': all_completed,
        }
    )

    if not created:
        summary.checked_in_count = checked_in_count
        summary.total_members = total_members
        if all_completed and not summary.streak_incremented:
            summary.streak_incremented = True
            streak_obj.current_streak += 1
            if streak_obj.current_streak > streak_obj.longest_streak:
                streak_obj.longest_streak = streak_obj.current_streak
            streak_obj.last_completed_date = target_date
            streak_obj.save()
        summary.save()
    elif all_completed:
        streak_obj.current_streak += 1
        if streak_obj.current_streak > streak_obj.longest_streak:
            streak_obj.longest_streak = streak_obj.current_streak
        streak_obj.last_completed_date = target_date
        streak_obj.save()

    return checked_in_count, total_members, all_completed
