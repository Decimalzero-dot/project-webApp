from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm 
from django.contrib.auth.views import LoginView
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
# Create your views here.

def user_login(request): 
    """
    Handles user login using Django's built-in AuthenticationForm.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            messages.success(request, f'Welcome back, {request.user.username}!')
            return redirect('accounts:login_success_redirect')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    context = {
        'title': 'User Login',
        'form': form,
    }
    # Assumes you have an accounts/login.html template
    return render(request, 'accounts/login.html', context)

def register_view(request):
    """
    Handles user registration (Client or Freelancer).
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately after registration (optional)
            # login(request, user) 
            
            messages.success(request, f'Account created for {user.username}! You can now log in.')
            
            # Redirect to the login page after successful registration
            return redirect('accounts:login') 
        else:
            # Add a general error message if form is invalid
            messages.error(request, 'Please correct the errors below.')
    else:
        # GET request: show a fresh form
        form = UserRegistrationForm()

    context = {
        'title': 'User Registration',
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

@login_required
def profile_view(request):
    """
    Allows the user to view and edit their profile details.
    """
    # In a real app, this is where profile form logic goes.
    context = {
        'title': f'{request.user.username}\'s Profile',
    }
    return render(request, 'accounts/profile.html', context)


def login_success_redirect(request):
    """
    Redirects the user to the appropriate dashboard based on their user_type.
    """
    if request.user.is_authenticated:
        if request.user.user_type == 1: # Client
            return redirect('clients:dashboard')
        elif request.user.user_type == 2: # Freelancer
            return redirect('freelancers:dashboard')
        else:
            # Fallback for unexpected user_type or future Admin type
            return redirect('accounts:profile')
    return redirect('accounts:login') # Should not happen if @login_required is used
# accounts/views.py (ADD THIS SIMPLE FUNCTION)

def unauthorized_view(request):
    """
    Simple view displayed when a user tries to access a page they don't have permission for.
    """
    context = {
        'title': 'Access Denied',
    }
    return render(request, 'accounts/unauthorized.html', context, status=403) # 403 Forbidden
# accounts/views.py

def welcome_view(request):
    """
    Landing page for unauthorized users.
    """
    # If the user is logged in, redirect them immediately to their dashboard
    if request.user.is_authenticated:
        return redirect('accounts:login_success_redirect')
        
    context = {
        'title': 'Welcome to Freelance Flow',
    }
    return render(request, 'accounts/welcome.html', context)