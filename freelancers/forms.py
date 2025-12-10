from django import forms
from .models import FreelancerProfile, Skill

# We use ModelMultipleChoiceField to handle the ManyToMany relationship with Skills
class FreelancerProfileForm(forms.ModelForm):
    """
    Form for freelancers to update their specialized profile and financial details.
    """
    # Allow the user to select multiple skills
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple, # Use checkboxes for selection
        required=False,
        label="Select your top skills"
    )

    class Meta:
        model = FreelancerProfile
        # FIX: Removed 'tier' from the editable fields. 'user' and 'tier' 
        # should generally be system-managed. We also switch to 'exclude' for clarity.
        exclude = ('user', 'tier') 
        
        # NOTE: If you decide the user *should* be able to set their tier, 
        # revert to your original 'fields' list and keep 'tier'.
        
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'A brief summary of your professional experience...'}),
            'hourly_rate': forms.NumberInput(attrs={'placeholder': 'e.g., 25.00', 'min': 0, 'step': 0.01}),
        }