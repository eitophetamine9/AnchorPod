from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    path('toggle/<int:goal_id>/', views.toggle_goal_view, name='toggle'),
    path('create/', views.create_goal_view, name='create'),
    path('edit/<int:goal_id>/', views.edit_goal_view, name='edit'),
    path('delete/<int:goal_id>/', views.delete_goal_view, name='delete'),
    path('export/', views.export_consistency_report_view, name='export'),
]
