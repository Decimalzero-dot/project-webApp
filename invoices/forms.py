from django import forms
from django.forms.models import inlineformset_factory
from .models import Invoice, InvoiceItem

# -----------------------------------------------
# 1. Main Invoice Form
# -----------------------------------------------
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        # Fields the freelancer needs to set manually
        fields = ['client', 'invoice_number', 'issue_date', 'due_date', 'tax_rate', 'task']
        widgets = {
            # Use date picker for a better UX
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        # We need the freelancer instance to limit choices later, 
        # but for simplicity now, we just call super.
        super().__init__(*args, **kwargs)
        
        # Example: Limit the task choices to tasks related to the current freelancer/client
        # self.fields['task'].queryset = Task.objects.filter(...)


# -----------------------------------------------
# 2. Invoice Item Formset
# -----------------------------------------------
# We use an inline formset to handle multiple InvoiceItem entries on the Invoice form.
InvoiceItemFormSet = inlineformset_factory(
    Invoice,             # The parent model
    InvoiceItem,         # The child model
    fields=('description', 'quantity', 'unit_price'),
    extra=1,             # Start with 1 empty item
    can_delete=True
)