from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

USER_TYPE_CHOICES = (
    (1, 'CLIENT'),
    (2, 'FREELANCER'),
)

class User(AbstractUser):
    """
    Custom User Model inheriting from AbstractUser to add user type roles.
    """
    email = models.EmailField(unique=True)
    
    # Field to distinguish between user types
    user_type = models.PositiveSmallIntegerField(
        choices=USER_TYPE_CHOICES,
        default=1,  # Default user type is CLIENT
        verbose_name='User Role'
    )

    # Required for Django to use the 'email' field for username validation
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    # Convenience properties for template/view logic
    @property
    def is_client(self):
        return self.user_type == 1

    @property
    def is_freelancer(self):
        return self.user_type == 2

    def __str__(self):
        return self.username