from django.urls import path
from .views import my_pod_view, update_matching_preferences_view

app_name = "pods"

urlpatterns = [
    path("", my_pod_view, name="my_pod"),
    path("preferences/", update_matching_preferences_view, name="preferences"),
]
