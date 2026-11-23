from django.urls import path
from .views import (
    my_pod_view,
    update_matching_preferences_view,
    pod_matching_view,
    pod_activity_view,
    pod_history_view,
)

app_name = "pods"

urlpatterns = [
    path("", my_pod_view, name="my_pod"),
    path("activity/", pod_activity_view, name="activity"),
    path("history/", pod_history_view, name="history"),
    path("match/", pod_matching_view, name="match"),
    path("preferences/", update_matching_preferences_view, name="preferences"),
]

