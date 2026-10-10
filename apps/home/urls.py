from django.urls import path
from .views import home_view, landing_view, check_in_view, nudge_view

app_name = "home"

urlpatterns = [
    path("", home_view, name="home"),
    path("landing/", landing_view, name="landing"),
    path("check-in/", check_in_view, name="check_in"),
    path("nudge/", nudge_view, name="nudge"),
]
