from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, USER_TYPE_CHOICES

class UserRegistrationForm(UserCreationForm):
    """
    A custom form for creating a new user, including the user_type field.
    """
    # Override the email field to make it required
    email = forms.EmailField(required=True)
    
    # Add the user_type field from the custom User model
    # We use a RadioSelect to make it clear and easy for the user to pick a role.
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial=1, # Default choice is CLIENT
        label="I am registering as a:"
    )

    class Meta(UserCreationForm.Meta):
        # Tell the form to use your custom User model
        model = User
        # Include all inherited fields plus the custom ones
        fields = UserCreationForm.Meta.fields + ('email', 'user_type',)
        
    def save(self, commit=True):
        """
        Saves the new user object with the correct user_type.
        """
        user = super().save(commit=False)
        # Manually set the user_type based on form input
        user.user_type = self.cleaned_data["user_type"]
        if commit:
            user.save()
        return user