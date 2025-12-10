from django.db import models
from django.conf import settings
from django_countries.fields import CountryField

# Create your models here.
User = settings.AUTH_USER_MODEL

# --- Choices for Profile Tier ---
TIER_CHOICES = (
    ('STANDARD', 'Standard'),
    ('PRO', 'Pro'),
    ('EXPERT', 'Expert'),
)

# --- Choices for Transaction Type ---
TRANSACTION_CHOICES = (
    ('PAYMENT', 'Payment Received (From Task)'),
    ('WITHDRAWAL', 'Withdrawal (To Bank)'),
)

class Skill(models.Model):
    """
    Tags used to categorize a freelancer's expertise (e.g., Python, Logo Design).
    """
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class FreelancerProfile(models.Model):
    """
    Profile extension for users who are freelancers (User.user_type = 2).
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 2}, # Ensures only Freelancer users can be linked
        primary_key=True
    )
    
    # Professional Details
    bio = models.TextField(blank=True, null=True, help_text="A short professional summary.")
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, 
                                      help_text="Your preferred hourly rate.")
    
    # Tier Status
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='STANDARD', 
                            help_text="The freelancer's current performance tier.")

    # Skills Many-to-Many Relationship
    skills = models.ManyToManyField(Skill, blank=True)

    # Financial Details (for withdrawal)
    account_name = models.CharField(max_length=150, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Freelancer Profile"
    
    class Meta:
        verbose_name = 'Freelancer Profile'
        verbose_name_plural = 'Freelancer Profiles'


class Transaction(models.Model):
    """
    Financial ledger for earnings and withdrawals for a freelancer.
    """
    profile = models.ForeignKey(
        FreelancerProfile, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Status for withdrawal requests (e.g., Pending, Completed, Failed)
    status = models.CharField(max_length=20, default='COMPLETED') 

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} for {self.profile.user.username}"

    class Meta:
        ordering = ['-timestamp']