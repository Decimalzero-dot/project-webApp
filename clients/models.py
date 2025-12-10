from django.db import models
from django.conf import settings
from django_countries.fields import CountryField

# Create your models here.

User = settings.AUTH_USER_MODEL

class Client(models.Model):
    """
    Profile extension for users who are clients (User.user_type = 1).
    Uses a OneToOneField linked to the User model.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        # Ensures that a Client Profile can only be created for a user 
        # whose role is CLIENT (1). We will create a Freelancer Profile later.
        limit_choices_to={'user_type': 1}, 
        primary_key=True
    )
    
    # Client-specific business details
    company_name = models.CharField(max_length=150, blank=True, null=True, 
                                    help_text="Name of the company or business.")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    
    # Placeholder for M-Pesa billing details for payment integration
    mpesa_paybill_number = models.CharField(max_length=20, blank=True, null=True, 
                                            verbose_name="M-Pesa Business/Paybill No.",
                                            help_text="Required for initiating payments via M-Pesa.")

    def __str__(self):
        return self.company_name or f"{self.user.username}'s Client Profile"
    
    class Meta:
        verbose_name = 'Client Profile'
        verbose_name_plural = 'Client Profiles'