from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

# Create your views here.
User = settings.AUTH_USER_MODEL

# We will create a custom decorator soon to enforce the 'is_client' check

@login_required
def dashboard_view(request):
    """
    The main landing page for authenticated clients.
    """
    # NOTE: You must implement a check here to ensure only clients can access this view
    if not request.user.is_client:
        # Redirect non-clients (e.g., freelancers) to their own dashboard or an error page
        return redirect('accounts:unauthorized') # Placeholder for an unauthorized view
    
    context = {
        'title': 'Client Dashboard',
        'active_tasks': 5, # Placeholder data
        'pending_payments': 2, # Placeholder data
    }
    return render(request, 'clients/dashboard.html', context)


@login_required
def freelancer_list_view(request):
    """
    Lists all registered freelancers for the client to discover and select.
    """
    if not request.user.is_client:
        return redirect('accounts:unauthorized')

    # Logic to fetch and filter Freelancer profiles will go here
    freelancers = [] # Placeholder list
    
    context = {
        'title': 'Discover Freelancers',
        'freelancers': freelancers,
    }
    return render(request, 'clients/freelancer_list.html', context)


@login_required
def task_post_view(request):
    """
    Allows the client to post a new task for bidding.
    """
    if not request.user.is_client:
        return redirect('accounts:unauthorized')

    context = {
        'title': 'Post a New Task',
    }
    return render(request, 'clients/task_post.html', context)