from django import forms
from .models import Task, Bid, TaskCategory
from freelancers.models import Skill # Import Skill for the ManyToMany field

class TaskCreateForm(forms.ModelForm):
    """
    Form for a Client to post a new job Task.
    """
    # Use ModelMultipleChoiceField for skills_required
    skills_required = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Required Skills (Select all that apply)"
    )

    class Meta:
        model = Task
        fields = [
            'title', 
            'description', 
            'category', 
            'skills_required', 
            'budget', 
            'due_date'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }
        
class BidCreateForm(forms.ModelForm):
    """
    Form for a Freelancer to submit a bid on an open Task.
    """
    class Meta:
        model = Bid
        fields = ['amount', 'delivery_days', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell the client why you are the best person for this task.'}),
            'amount': forms.NumberInput(attrs={'placeholder': 'Your total charge (KSh)'}),
            'delivery_days': forms.NumberInput(attrs={'placeholder': 'Days to complete'}),
        }