import csv
from collections import defaultdict
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from apps.home.models import DailyCheckIn
from apps.pods.services import get_or_create_user_pod
from .models import SelfCareGoal, DailyGoalCompletion
from .services import toggle_goal_completion, create_custom_goal, delete_goal, update_custom_goal


@login_required
@require_POST
def toggle_goal_view(request, goal_id):
    completion, is_completed, completed_count, total_count, error = toggle_goal_completion(
        user=request.user,
        goal_id=goal_id
    )

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")

    if error:
        if is_ajax:
            return JsonResponse({"success": False, "error": error}, status=400)
        messages.error(request, error)
        return redirect("home:home")

    if is_ajax:
        return JsonResponse({
            "success": True,
            "goal_id": goal_id,
            "completed": is_completed,
            "completed_count": completed_count,
            "total_count": total_count,
        })

    return redirect("home:home")


@login_required
@require_POST
def create_goal_view(request):
    title = request.POST.get("title", "")
    category = request.POST.get("category", "wellness")

    goal, error = create_custom_goal(user=request.user, title=title, category=category)

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")

    if error:
        if is_ajax:
            return JsonResponse({"success": False, "error": error}, status=400)
        messages.error(request, error)
        return redirect("home:home")

    success_msg = f'Small win "{goal.title}" added to your daily rhythm.'
    if is_ajax:
        return JsonResponse({
            "success": True,
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "category": goal.category,
                "completed": False,
            },
            "message": success_msg,
        })

    messages.success(request, success_msg)
    return redirect("home:home")


@login_required
@require_POST
def delete_goal_view(request, goal_id):
    success, error = delete_goal(user=request.user, goal_id=goal_id)

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")

    if error:
        if is_ajax:
            return JsonResponse({"success": False, "error": error}, status=400)
        messages.error(request, error)
        return redirect("home:home")

    if is_ajax:
        return JsonResponse({"success": True, "goal_id": goal_id})

    messages.success(request, "Habit removed from your daily list.")
    return redirect("home:home")


@login_required
@require_POST
def edit_goal_view(request, goal_id):
    title = request.POST.get("title", "")
    category = request.POST.get("category", None)

    goal, error = update_custom_goal(user=request.user, goal_id=goal_id, title=title, category=category)

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")

    if error:
        if is_ajax:
            return JsonResponse({"success": False, "error": error}, status=400)
        messages.error(request, error)
        return redirect("home:home")

    if is_ajax:
        return JsonResponse({
            "success": True,
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "category": goal.category,
            },
            "message": "Habit updated successfully.",
        })

    messages.success(request, "Habit updated successfully.")
    return redirect("home:home")


@login_required
def export_consistency_report_view(request):
    """
    Generates and downloads a CSV consistency report summarizing the student's
    daily attendance check-ins, habit completion metrics, and active pod context.
    """
    user = request.user
    today = date.today()
    pod = get_or_create_user_pod(user)

    # Fetch all check-in dates
    checkin_dates = set(
        DailyCheckIn.objects.filter(user=user).values_list("date", flat=True)
    )

    # Fetch all completions for the user
    completions = list(
        DailyGoalCompletion.objects.filter(user=user)
        .select_related("goal")
        .order_by("-date")
    )

    # Total active goals count
    total_active_goals = SelfCareGoal.objects.filter(user=user, is_active=True).count() or 1

    # Group completions by date
    date_completions = defaultdict(list)
    for c in completions:
        date_completions[c.date].append(c)

    all_dates = sorted(set(list(checkin_dates) + list(date_completions.keys())), reverse=True)
    if not all_dates:
        all_dates = [today]

    response = HttpResponse(content_type="text/csv")
    filename = f"AnchorPod_Consistency_{user.username}_{today.strftime('%Y%m%d')}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        "Date",
        "Username",
        "Pod Name",
        "Daily Check-In",
        "Completed Habits",
        "Habits Completed Count",
        "Total Active Habits",
        "Completion Rate (%)",
    ])

    for d in all_dates:
        checked_in = "Yes" if d in checkin_dates else "No"
        done_goals = [c.goal.title for c in date_completions.get(d, []) if c.completed]
        done_count = len(done_goals)
        rate = round((done_count / total_active_goals) * 100, 1)
        habits_str = "; ".join(done_goals) if done_goals else "None recorded"

        writer.writerow([
            d.strftime("%Y-%m-%d"),
            user.username,
            pod.name,
            checked_in,
            habits_str,
            done_count,
            total_active_goals,
            f"{rate}%",
        ])

    return response
