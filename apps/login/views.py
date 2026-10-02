from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home:home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("home:home")
        return render(request, "login/login.html", {
            "error": "Invalid username/email or password.",
            "username": username,
        })
    return render(request, "login/login.html")


def logout_view(request):
    logout(request)
    return redirect("login:login")
