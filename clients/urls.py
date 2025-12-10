from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    # Main Dashboard for Clients after login
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # View to list available Freelancers for discovery
    path('freelancers/', views.freelancer_list_view, name='freelancer_list'),
    
    # View to post a new task (to be implemented later)
    path('post-task/', views.task_post_view, name='task_post'),
]