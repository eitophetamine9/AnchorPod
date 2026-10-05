from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from .services import send_anonymous_nudge, mark_nudge_read


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

    if is_ajax:
        return JsonResponse({"success": marked})

    return redirect("home:home")
