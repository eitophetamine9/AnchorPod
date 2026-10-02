from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from apps.profile.models import Profile
from apps.user_settings.models import UserSettings


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home:home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        # Support both 'password' and Django's form 'password1'/'password2'
        password = request.POST.get("password") or request.POST.get("password1", "")
        password_confirm = request.POST.get("password2") or password

        if not username:
            return render(request, "register/register.html", {
                "error": "University email or username is required."
            })

        if User.objects.filter(username=username).exists():
            return render(request, "register/register.html", {
                "error": "Username or email already exists.",
                "username": username,
            })

        if password != password_confirm:
            return render(request, "register/register.html", {
                "error": "Passwords do not match.",
                "username": username,
            })

        if len(password) < 8:
            return render(request, "register/register.html", {
                "error": "Password must be at least 8 characters.",
                "username": username,
            })

        # Create user
        user = User.objects.create_user(username=username, password=password)

        initial = username[:1].upper() if username else "A"
        nickname = f"Anchor {initial}"
        default_goals = ['Drink water', 'Step outside', 'Study for 25 minutes']

        # Initialize Profile
        Profile.objects.get_or_create(
            user=user,
            defaults={
                'nickname': nickname,
                'goals': default_goals,
            }
        )

        # Initialize UserSettings
        UserSettings.objects.get_or_create(user=user)

        messages.success(request, "Registration Successful")
        return redirect("login:login")

    return render(request, "register/register.html")
