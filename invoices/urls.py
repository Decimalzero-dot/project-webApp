# invoices/urls.py

from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    # --- INVOICE CRUD VIEWS ---
    
    # 1. Invoice List (The primary view for the app root)
    path('', views.InvoiceListView.as_view(), name='invoice_list'), 
    
    # 2. Invoice Creation (Using the function-based view for FormSet)
    path('create/', views.invoice_create_view, name='invoice_create'), 
    
    # 3. Invoice Detail View 
    path('<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'), 
    
    
    # --- MPESA TRANSACTION VIEWS ---
    
    # 4. Payment Initiation Landing Page (This is your views.index function)
    # RENAME: Now accessed at /invoices/checkout/
    path('checkout/', views.index, name='checkout_initiate'), 
    
    # 5. STK Push Initiation (The function that executes the M-Pesa API request)
    path('stk-push/', views.stk_push, name='stk_push'),
    
    # 6. Waiting Page 
    path('waiting/<int:transaction_id>/', views.waiting_page, name='waiting_page'),
    
    # 7. M-Pesa Callback 
    path('callback/', views.callback, name='callback'),
    
    # 8. Status Check 
    path('check-status/<int:transaction_id>/', views.check_status, name='check_status'),
    
    # 9. Result Pages
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('payment-cancelled/', views.payment_cancelled, name='payment_cancelled'), 
]