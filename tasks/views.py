from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

# Create your views here.
# Import models/forms from local and external apps
from .models import Task, Bid, TaskSubmission
from .forms import TaskCreateForm, BidCreateForm
from freelancers.models import FreelancerProfile # Needed for skill matching

# Placeholder decorator functions (assume they are defined or imported)
def client_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_client:
            messages.error(request, "Access restricted to Clients.")
            return redirect('accounts:unauthorized') 
        return view_func(request, *args, **kwargs)
    return wrapper

def freelancer_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_freelancer:
            messages.error(request, "Access restricted to Freelancers.")
            return redirect('accounts:unauthorized') 
        return view_func(request, *args, **kwargs)
    return wrapper

# --- CLIENT-SIDE VIEWS ---

@client_required
def client_task_list_view(request):
    """ Client dashboard view of all tasks they have posted. """
    tasks = Task.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'tasks/client_task_list.html', {'tasks': tasks, 'title': 'My Posted Tasks'})

@client_required
def task_create_view(request):
    """ Allows Client to create and post a new task. """
    if request.method == 'POST':
        form = TaskCreateForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.client = request.user # Assign the current user (client)
            task.save()
            form.save_m2m() # Save ManyToMany relationships (skills_required)
            messages.success(request, f'Task "{task.title}" has been successfully posted!')
            return redirect('tasks:client_task_list')
    else:
        form = TaskCreateForm()
        
    return render(request, 'tasks/task_create.html', {'form': form, 'title': 'Post New Task'})

# ... (accept_bid_view will be complex, let's keep it placeholder for now) ...
@client_required
def accept_bid_view(request, pk, bid_pk):
    messages.info(request, "Placeholder: Logic to accept bid and change task status.")
    return redirect('tasks:task_detail', pk=pk) 


# --- FREELANCER-SIDE VIEWS ---

@freelancer_required
def available_tasks_list_view(request):
    """ 
    Lists tasks that are 'OPEN' and match the freelancer's skills.
    This is the core skill-matching view.
    """
    profile = get_object_or_404(FreelancerProfile, user=request.user)
    freelancer_skills = profile.skills.all()
    
    # 1. Start with tasks that are OPEN
    open_tasks = Task.objects.filter(status='OPEN')
    
    # 2. Filter tasks based on the freelancer's skills.
    # The Q object (OR condition) finds tasks that require AT LEAST ONE of the freelancer's skills.
    # We use a distinct query to ensure we don't return duplicates if a task matches multiple skills.
    
    # Create an initial empty Q object
    skill_filter = Q()
    for skill in freelancer_skills:
        skill_filter |= Q(skills_required__in=[skill])
        
    # Apply the skill filter and ensure the task is currently open
    matching_tasks = open_tasks.filter(skill_filter).distinct().order_by('-created_at')
    
    # Optionally, get tasks that the freelancer has already bid on to exclude them from the list
    bids_made = Bid.objects.filter(freelancer=profile).values_list('task__pk', flat=True)
    final_tasks = matching_tasks.exclude(pk__in=bids_made)

    context = {
        'title': 'Available Jobs Matching Your Skills',
        'tasks': final_tasks,
        'has_skills': freelancer_skills.exists(),
    }
    return render(request, 'tasks/available_tasks_list.html', context)


@freelancer_required
def bid_create_view(request, pk):
    """ Allows Freelancer to submit a Bid on an open Task. """
    task = get_object_or_404(Task, pk=pk, status='OPEN')
    freelancer_profile = get_object_or_404(FreelancerProfile, user=request.user)

    if request.method == 'POST':
        form = BidCreateForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.task = task
            bid.freelancer = freelancer_profile
            
            # Check for existing bid (prevent unique_together error)
            if Bid.objects.filter(task=task, freelancer=freelancer_profile).exists():
                messages.error(request, "You have already placed a bid on this task.")
            else:
                bid.save()
                messages.success(request, "Your bid has been successfully placed!")
            
            return redirect('tasks:task_detail', pk=pk)
    else:
        form = BidCreateForm()
        
    context = {
        'title': f'Bid on: {task.title}',
        'task': task,
        'form': form,
    }
    return render(request, 'tasks/bid_create.html', context)


# --- SHARED VIEWS ---

@login_required
def task_detail_view(request, pk):
    """ Shows the detail of a task to the client or involved freelancer. """
    task = get_object_or_404(Task, pk=pk)
    
    is_client = request.user == task.client
    is_involved_freelancer = Bid.objects.filter(task=task, is_accepted=True, freelancer__user=request.user).exists()
    
    if not is_client and not is_involved_freelancer:
        # If the task is OPEN, any freelancer can view it
        if task.status != 'OPEN' or not request.user.is_freelancer:
            messages.error(request, "You do not have permission to view this task.")
            return redirect('homepage')
            
    bids = task.bids.all().order_by('amount') # Show bids for client

    context = {
        'title': task.title,
        'task': task,
        'is_client': is_client,
        'bids': bids,
    }
    return render(request, 'tasks/task_detail.html', context)