
from django.urls import path
from . import views

app_name = 'freelancers'

urlpatterns = [
    # Main Dashboard 
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Profile CRUD
    path('profile/update/', views.profile_update_view, name='profile_update'),
    path('profile/<str:username>/', views.profile_detail_view, name='profile_detail'),
    
    # Financial Views
    path('balance/', views.balance_view, name='balance'),
    path('withdrawal/request/', views.withdrawal_request_view, name='withdrawal_request'),
    
    # Tasks/Bidding Views
    path('tasks/', views.available_tasks_view, name='available_tasks'),
    
    # Placeholder for unauthorized access (if needed)
    # path('unauthorized/', views.unauthorized_view, name='unauthorized'),
]