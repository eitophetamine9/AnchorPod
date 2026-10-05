from django.urls import path
from . import views

app_name = 'nudges'

urlpatterns = [
    path('send/', views.send_nudge_view, name='send'),
    path('dismiss/<int:nudge_id>/', views.dismiss_nudge_view, name='dismiss'),
]
