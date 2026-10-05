from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from .services import toggle_goal_completion, create_custom_goal, delete_goal


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
