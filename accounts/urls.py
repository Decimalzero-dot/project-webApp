from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView 
from django.contrib.auth import views as auth_views
from . import views # We will use this for custom views later

app_name = 'accounts'

urlpatterns = [
    # AUTHENTICATION VIEWS
    path('login/', views.user_login, name='login'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    # PLACEHOLDER: Registration and Profile views to be implemented later
    path('register/', views.register_view, name='register'), # We need to create this view
    path('profile/', views.profile_view, name='profile'),   # We need to create this view
    
    # PASSWORD RESET VIEWS (Required for your login template links)
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            email_template_name='accounts/password_reset_email.html',
            success_url=reverse_lazy('accounts:password_reset_done')
        ),
        name='password_reset'
    ),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url=reverse_lazy('accounts:password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

     # 1. Registration
    path('register/', views.register_view, name='register'),
    
    # 2. Login (using the new function we defined)
    path('login/', views.user_login, name='login'), # <-- Check this URL name is 'login'
    
    # 3. Logout (using Django's built-in class)
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'), # Redirects to homepage after logout
    
    # 4. Dashboard Redirector (Used by base.html and post-login logic)
    path('dashboard/redirect/', views.login_success_redirect, name='login_success_redirect'), 
    
    # 5. Profile View (basic profile view)
    path('profile/', views.profile_view, name='profile'),
    
    # 6. Unauthorized Access (Useful for decorators)
    path('unauthorized/', views.unauthorized_view, name='unauthorized'), 

]

