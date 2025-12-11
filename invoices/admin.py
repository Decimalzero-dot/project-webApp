from django.contrib import admin
from .models import Invoice, InvoiceItem
from .models import Transactions
# Register your models here.


# Register your models here.
@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'phone_number', 'amount','status','date_created','mpesa_receipt_number')
    list_filter = ('status', 'date_created','transaction_id')
    search_fields = ('transaction_id', 'phone_number', 'amount','status','date_created','mpesa_receipt_number')
    
    def formatted_amount(self, obj):
        return f"Ksh {obj.amount:,.2f}"
    formatted_amount.short_description = "Amount"
# -----------------------------------------------
# Inline for Invoice Items (Line Items)
# -----------------------------------------------

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    fields = ('description', 'quantity', 'unit_price', 'total_price')
    readonly_fields = ('total_price',)
    extra = 2

# -----------------------------------------------
# Main Invoice Admin
# -----------------------------------------------
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'freelancer', 'client', 'issue_date', 'due_date', 'total_amount', 'status')
    list_filter = ('status', 'issue_date', 'due_date')
    search_fields = ('invoice_number', 'client__username', 'freelancer__username')
    date_hierarchy = 'issue_date'
    
    # Add the InvoiceItemInline to the main Invoice form
    inlines = [InvoiceItemInline]
    
    # Group fields for better display in the form
    fieldsets = (
        (None, {
            'fields': ('invoice_number', 'status', 'task')
        }),
        ('Parties', {
            'fields': ('freelancer', 'client'),
        }),
        ('Financial Details', {
            'fields': ('issue_date', 'due_date', 'subtotal', 'tax_rate', 'total_amount'),
            # Make the calculated totals read-only
            'readonly_fields': ('subtotal', 'total_amount'),
        }),
    )
    