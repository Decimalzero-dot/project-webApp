from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # --- CLIENT-SIDE VIEWS ---
    # The client's view to list tasks they have posted
    path('my-tasks/', views.client_task_list_view, name='client_task_list'),
    
    # URL used by the Client (from the client_portal) to post a new task
    path('post/', views.task_create_view, name='task_create'),
    
    # URL used by the Client to accept a specific bid
    path('<int:pk>/accept-bid/<int:bid_pk>/', views.accept_bid_view, name='accept_bid'),
    
    # --- FREELANCER-SIDE VIEWS ---
    # The task list filtered by the freelancer's skills
    path('available/', views.available_tasks_list_view, name='available_tasks_list'),
    
    # URL to submit a bid on a task
    path('<int:pk>/bid/', views.bid_create_view, name='bid_create'),
    
    # --- SHARED VIEWS ---
    # Detail view for a specific task (viewable by client or involved freelancer)
    path('<int:pk>/', views.task_detail_view, name='task_detail'),
]