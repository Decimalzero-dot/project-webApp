from django import forms
from .models import Client

class ClientProfileForm(forms.ModelForm):
    """
    Form for clients to update their specialized profile details.
    """
    class Meta:
        model = Client
        fields = [
            'company_name',
            'phone_number',
            'country',
            'mpesa_paybill_number',
        ]
        
        widgets = {
            'company_name': forms.TextInput(attrs={'placeholder': 'Your Company Name (Optional)'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g., +254 7XX XXX XXX'}),
            'mpesa_paybill_number': forms.TextInput(attrs={'placeholder': 'Your M-Pesa Paybill or Business Number'}),
        }
        
        labels = {
            'mpesa_paybill_number': 'M-Pesa Paybill / Business Number',
        }