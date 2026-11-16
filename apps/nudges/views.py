from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from .models import Nudge, NudgeTemplate
from .services import send_anonymous_nudge, mark_nudge_read


@login_required
def nudge_vault_view(request):
    """
    Displays the student's personal Encouragement Vault, archiving all
    received peer nudges and affirmations with filter options and vault statistics.
    """
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "mark_all_read":
            Nudge.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
            messages.success(request, "All received encouragements have been marked as read.")
            return redirect("nudges:vault")

    view_mode = request.GET.get("filter", "received")
    selected_category = request.GET.get("category", "all")

    if view_mode == "sent":
        nudges_qs = Nudge.objects.filter(sender=request.user).select_related(
            "template", "pod"
        ).order_by("-sent_at")
    else:
        view_mode = "received"
        nudges_qs = Nudge.objects.filter(recipient=request.user).select_related(
            "template", "pod"
        ).order_by("-sent_at")

    if selected_category and selected_category != "all":
        nudges_qs = nudges_qs.filter(template__category=selected_category)

    total_received = Nudge.objects.filter(recipient=request.user).count()
    unread_received = Nudge.objects.filter(recipient=request.user, is_read=False).count()
    total_sent = Nudge.objects.filter(sender=request.user).count()

    categories = [
        {"id": "all", "label": "All Messages"},
        {"id": "gentle", "label": "Gentle Reminders"},
        {"id": "wellness", "label": "Wellness & Breath"},
        {"id": "calm", "label": "Calm Energy"},
        {"id": "encouragement", "label": "Encouragement"},
        {"id": "solidarity", "label": "Pod Solidarity"},
    ]

    context = {
        "nudges": nudges_qs,
        "view_mode": view_mode,
        "selected_category": selected_category,
        "total_received": total_received,
        "unread_received": unread_received,
        "total_sent": total_sent,
        "categories": categories,
    }
    return render(request, "nudges/vault.html", context)


@login_required
@require_POST
def send_nudge_view(request):
    recipient_id = request.POST.get("recipient_id")
    template_id = request.POST.get("template_id")

    nudge, error = send_anonymous_nudge(request.user, recipient_id, template_id)

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")

    if error:
        if is_ajax:
            return JsonResponse({"success": False, "error": error}, status=400)
        messages.error(request, error)
        return redirect("home:home")

    success_msg = "Your anonymous nudge has been sent. Small reminders make a big difference."
    if is_ajax:
        return JsonResponse({"success": True, "message": success_msg})

    messages.success(request, success_msg)
    return redirect("home:home")


@login_required
@require_POST
def dismiss_nudge_view(request, nudge_id):
    marked = mark_nudge_read(request.user, nudge_id)
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")

    next_url = request.POST.get("next")
    if is_ajax:
        return JsonResponse({"success": marked})

    if next_url:
        return redirect(next_url)
    return redirect("home:home")
