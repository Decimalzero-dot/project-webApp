from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import FreelancerProfile
from .forms import FreelancerProfileForm # Import the new form


# --- Custom Decorator ---
# Assuming 'is_freelancer' is a method/property on your custom User model
def freelancer_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'is_freelancer') or not request.user.is_freelancer:
            messages.error(request, "You must be logged in as a Freelancer to access this page.")
            return redirect('accounts:unauthorized') # Adjust this URL as necessary
        return view_func(request, *args, **kwargs)
    return wrapper


@freelancer_required
def dashboard_view(request):
    """
    The main landing page for authenticated freelancers.
    Includes logic to check for profile completeness.
    """
    # Use get_or_create to ensure the profile exists before proceeding
    profile, created = FreelancerProfile.objects.get_or_create(user=request.user)
    
    # Check if the profile is complete (e.g., has skills, rate, and bio)
    is_profile_complete = (
        profile.skills.exists() and 
        profile.hourly_rate is not None and 
        profile.bio
    )
    
    if not is_profile_complete:
        # The warning message seen in the screenshot
        messages.warning(request, "Your profile is incomplete! Please update your skills and details to start bidding on tasks.")
        # FIX: The dashboard redirects to the update page if incomplete
        return redirect('freelancers:profile_update') 
        
    context = {
        'title': 'Freelancer Dashboard',
        'profile': profile,
        'completed_tasks': 12, # Placeholder metric
        'current_balance': 4500.00, # Placeholder metric
    }
    return render(request, 'freelancers/dashboard.html', context)


@freelancer_required
def profile_update_view(request):
    """
    Allows the freelancer to create or update their professional profile.
    FIX: Uses try/except to robustly handle profile creation (first time) 
    and update (subsequent times).
    """
    try:
        # Try to get the existing profile
        profile = request.user.freelancerprofile
    except FreelancerProfile.DoesNotExist:
        # If it doesn't exist, create an UN-SAVED instance linked to the user
        profile = FreelancerProfile(user=request.user) 

    if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            
            # --- CRITICAL REDIRECTION FIX ---
            # Now redirect to the DETAIL page, which forces a fresh load of the saved data.
            return redirect('freelancers:profile_detail', username=request.user.username)    

    if request.method == 'POST':
        # Pass request.FILES for potential image uploads
        form = FreelancerProfileForm(request.POST, request.FILES, instance=profile) 
        
        if form.is_valid():
            # form.save() handles both CREATE (if profile is new) and UPDATE (if profile exists)
            form.save()
            messages.success(request, 'Profile updated successfully!')
            
            # FIX: Redirect to the dashboard (which will re-check profile completeness)
            return redirect('freelancers:dashboard')
    else:
        # GET request: form is initialized with the latest DB data
        form = FreelancerProfileForm(instance=profile)

    context = {
        'title': 'Update Profile',
        'form': form,
    }
    return render(request, 'freelancers/profile_update.html', context)


@freelancer_required
def profile_update_view(request):
    try:
        profile = request.user.freelancerprofile
    except FreelancerProfile.DoesNotExist:
        profile = FreelancerProfile(user=request.user)

    if request.method == 'POST':
        form = FreelancerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            # Redirect to dashboard or detail page
            return redirect('freelancers:dashboard')  
    else:
        form = FreelancerProfileForm(instance=profile)

    context = {
        'title': 'Update Profile',
        'form': form,
    }
    return render(request, 'freelancers/profile_update.html', context)
    return redirect('freelancers:profile_detail', username=request.user.username)


@freelancer_required
def balance_view(request):
    """
    Shows the freelancer's transaction history and current balance.
    """
    profile = get_object_or_404(FreelancerProfile, user=request.user)
    transactions = profile.transactions.all() 
    
    # Simple balance calculation
    balance = 0
    for t in transactions:
        if t.transaction_type == 'PAYMENT':
            balance += t.amount
        elif t.transaction_type == 'WITHDRAWAL':
            balance -= t.amount

    context = {
        'title': 'Account Balance & History',
        'transactions': transactions,
        'current_balance': balance,
        'profile': profile,
    }
    return render(request, 'freelancers/balance.html', context)


# Placeholder for other views
@freelancer_required
def withdrawal_request_view(request):
    return render(request, 'freelancers/withdrawal_request.html', {'title': 'Request Withdrawal'})

@freelancer_required
def available_tasks_view(request):
    return render(request, 'freelancers/available_tasks.html', {'title': 'Available Tasks'})