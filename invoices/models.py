from django.db import models
from django.conf import settings
from tasks.models import Task # CRITICAL: Imports the Task model from the tasks app

# Access the Custom User model
# Create your models here.
class Transactions(models.Model):
    # transaction id : mpesa's valid transaction id for successfull payments 
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # mpesa receipt number 
    mpesa_receipt_number = models.CharField(max_length=100, blank=True, null=True)
    # pending / complete 
    status = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True) # true date / time / apps perspective 
    date_created = models.DateTimeField(auto_now_add=True) # date of capture server perspective
    email = models.EmailField(blank=True,null=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    
    def __str__(self):
        print(f"Transaction- {self.mpesa_receipt_number}- {self.status}- {self.date_created}")
        return f"Transaction- {self.mpesa_receipt_number}- {self.status}- {self.date_created}"
User = settings.AUTH_USER_MODEL 

class Invoice(models.Model):
    ## Status Choices
    STATUS_DRAFT = 1
    STATUS_SENT = 2
    STATUS_PAID = 3
    STATUS_OVERDUE = 4
    STATUS_VOID = 5
    
    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SENT, 'Sent'),
        (STATUS_PAID, 'Paid'),
        (STATUS_OVERDUE, 'Overdue'),
        (STATUS_VOID, 'Void'),
    )

    ## Core Relationships
    # Client is the user receiving the invoice
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices_issued_to')
    # Freelancer is the user issuing the invoice (current user creating it)
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices_issued_by')
    
    # Optional link to the Task this invoice is for
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)

    ## Invoice Details
    invoice_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_DRAFT)
    
    ## Financial Details (Calculated based on InvoiceItems)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) # e.g., 0.10 for 10%
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    ## Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-issue_date', 'invoice_number']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'

    def __str__(self):
        return f"Invoice #{self.invoice_number} ({self.get_status_display()})"
    
    # Method to calculate total based on items (called by InvoiceItem's save method)
    def calculate_totals(self):
        # Calculates subtotal from all related items
        self.subtotal = sum(item.total_price for item in self.items.all())
        
        # Calculate tax amount
        tax_amount = self.subtotal * self.tax_rate
        
        # Calculate final total
        self.total_amount = self.subtotal + tax_amount
        self.save()


class InvoiceItem(models.Model):
    ## Relationship to the main Invoice
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    
    ## Item Details
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    ## Calculated Field
    # total_price is calculated automatically when saving
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)

    class Meta:
        verbose_name = 'Invoice Item'
        verbose_name_plural = 'Invoice Items'

    def __str__(self):
        return f"{self.description} on Invoice #{self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        # 1. Calculate total price before saving the item
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # 2. Recalculate the parent invoice totals
        # Avoids infinite recursion during updates by checking 'update_parent'
        if not kwargs.get('update_parent', False): 
            self.invoice.calculate_totals()