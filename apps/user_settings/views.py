from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserSettings


@login_required
def settings_view(request):
    settings, _ = UserSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        settings.dark_mode = "dark_mode" in request.POST
        settings.email_notifications = "email_notifications" in request.POST
        settings.receive_nudges = "receive_nudges" in request.POST
        settings.save()
        messages.success(request, "Your preferences have been saved.")
        return redirect("user_settings:settings")

    return render(request, "user_settings/settings.html", {
        "settings": settings,
    })
