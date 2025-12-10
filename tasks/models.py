# tasks/models.py (FIXED AND CONSOLIDATED)

from django.db import models
from django.conf import settings
# NOTE: Removed 'from .models import TaskCategory' to fix the circular import.

# Get Custom User model
User = settings.AUTH_USER_MODEL

# -----------------------------------------------
# 1. STATUS CHOICES
# -----------------------------------------------
STATUS_CHOICES = (
    ('OPEN', 'Open for Bids'),
    ('BID_ACCEPTED', 'Bid Accepted'),
    ('IN_PROGRESS', 'In Progress'),
    ('UNDER_REVIEW', 'Under Review'),
    ('COMPLETED', 'Completed'),
    ('PAID', 'Paid'),
    ('CANCELLED', 'Cancelled'),
)

# -----------------------------------------------
# 2. TASK CATEGORY (Must be defined first)
# -----------------------------------------------
class TaskCategory(models.Model):
    """
    Defines the categories that tasks can be assigned to (e.g., Web Design, Copywriting).
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon_class = models.CharField(max_length=50, blank=True, null=True) 

    class Meta:
        verbose_name_plural = "Task Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

# -----------------------------------------------
# 3. TASK MODEL (Consolidated definition)
# -----------------------------------------------
class Task(models.Model):
    """
    The main job posting model created by the Client.
    """
    # Core Details
    title = models.CharField(max_length=255)
    description = models.TextField(verbose_name="Detailed requirements of the task")
    
    # Relationships
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posted_tasks',
        # Removed limit_choices_to for now. It's better handled in forms/admin.
    )
    freelancer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tasks', # User assigned to the task
        # Removed limit_choices_to for now.
    )

    # Categorization and Skill Matching
    category = models.ForeignKey(
        'TaskCategory',             # CRITICAL: Use string reference
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='tasks'
    )
    skills_required = models.ManyToManyField(
        'freelancers.Skill',        # CRITICAL: Use string reference to external app
        help_text="Skills needed to complete the task."
    )
    
    # Compensation and Deadline
    budget = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Budget Amount"
    )
    due_date = models.DateTimeField(null=True, blank=True) # Set to nullable until form is ready
    
    # Workflow Status
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='OPEN'
    )
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

# -----------------------------------------------
# 4. BID MODEL
# -----------------------------------------------
class Bid(models.Model):
    """
    An offer made by a Freelancer on a specific Task.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='bids')
    freelancer = models.ForeignKey(
        'freelancers.FreelancerProfile', # CRITICAL: String reference
        on_delete=models.CASCADE,
        related_name='task_bids'
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="The amount the freelancer is charging.")
    delivery_days = models.IntegerField(help_text="Estimated number of days to complete.")
    message = models.TextField(blank=True, help_text="A cover letter explaining why you are the best fit.")
    
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # NOTE: You must use self.freelancer.user.username once the profile exists
        return f"Bid on {self.task.title}"
    
    class Meta:
        unique_together = ('task', 'freelancer')

# -----------------------------------------------
# 5. TASK SUBMISSION MODEL
# -----------------------------------------------
class TaskSubmission(models.Model):
    """
    Record of the final work submitted by the Freelancer for Client review.
    """
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='submission')
    freelancer = models.ForeignKey('freelancers.FreelancerProfile', on_delete=models.CASCADE) # CRITICAL: String reference
    
    # Deliverable Details
    delivery_file = models.FileField(upload_to='submissions/%Y/%m/%d/', blank=True, null=True) 
    delivery_link = models.URLField(max_length=500, blank=True, null=True, help_text="Link to the final deliverable (e.g., Google Drive).")
    notes = models.TextField(blank=True)
    
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission for {self.task.title}"