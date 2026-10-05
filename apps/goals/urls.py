from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    path('toggle/<int:goal_id>/', views.toggle_goal_view, name='toggle'),
    path('create/', views.create_goal_view, name='create'),
    path('delete/<int:goal_id>/', views.delete_goal_view, name='delete'),
]
