# invoices/views.py

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db import transaction
from .models import Transactions, Invoice
from .forms import InvoiceForm, InvoiceItemFormSet # Assuming these exist
import requests # API interaction 
from django.db.models.expressions import result
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse # json format 
import base64 # encryption
from datetime import datetime
import json
from django.core.mail import send_mail
from django.core.paginator import Paginator
import os
from dotenv import load_dotenv


load_dotenv() # making our settings config available to our view files 


# -----------------------------------------------
# CONFIGURATION & HELPER FUNCTIONS (MPESA)
# -----------------------------------------------

# Environment Variables should be set in .env file
SHORTCODE = os.getenv('SHORTCODE')
PASSKEY = os.getenv('PASSKEY')
BASE_URL = os.getenv('BASE_URL')
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
NGROK_URL = os.getenv('NGROK_URL')
CALLBACK_URL = os.getenv('CALLBACK_URL') # Assumes this is the base NGROK/public URL

class MpesaPassword:
    @staticmethod 
    def generate_security_credential():
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = SHORTCODE + PASSKEY + timestamp
        online_password = base64.b64encode(data_to_encode.encode()).decode()
        return online_password

def generate_access_token():
    auth_url = f'{BASE_URL}/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(auth_url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    return response.json().get('access_token')

# -----------------------------------------------
# MPESA TRANSACTION VIEWS
# -----------------------------------------------

# index page for transactions (checkout initiation form)
def index(request):
    return render(request, 'invoices/index.html')

@csrf_exempt 
def stk_push(request):
    if request.method == 'POST':
        # Capturing form details
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        # Create initial PENDING transaction record
        transaction = Transactions.objects.create(
            phone_number=phone,
            amount=amount,
            status="Pending",
            description="Awaiting status result",
            name=name,
            email=email,
        )
        
        access_token = generate_access_token()
        stk_url = f'{BASE_URL}/mpesa/stkpush/v1/processrequest'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f'{SHORTCODE}{PASSKEY}{timestamp}'.encode()).decode()

        payload = {
            "BusinessShortCode": SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": SHORTCODE,
            "PhoneNumber" : phone,
            "CallBackURL": f"{CALLBACK_URL}invoices/callback/",
            "AccountReference": f"Transaction_{transaction.id}",
            "TransactionDesc": "Payment for Services"
        }
        
        response = requests.post(stk_url, json=payload, headers=headers)
        response_data = response.json()

        transaction_id = response_data.get('CheckoutRequestID', None)
        transaction.transaction_id = transaction_id
        transaction.description = response_data.get('ResponseDescription', "No Description")
        transaction.save()
        
        return redirect('invoices:waiting_page', transaction_id=transaction.id)

    return JsonResponse({'error': "invalid request"}, status=400)

def waiting_page(request, transaction_id):
    transaction = Transactions.objects.get(id=transaction_id)
    return render(request, 'invoices/waiting.html',{'transaction_id': transaction_id})

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stk_callback = data.get('Body',{}).get('stkCallback',{})
            result_code = stk_callback.get('ResultCode',None)
            result_desc = stk_callback.get('ResultDesc','')
            transaction_id = stk_callback.get('CheckoutRequestID',None)

            if transaction_id:
                transaction = Transactions.objects.filter(transaction_id=transaction_id).first()
                
                if transaction:
                    if result_code == 0: # Success
                        callback_metadata = stk_callback.get('CallbackMetadata',{}).get('Item',[])
                        receipt_number = next((item.get('Value') for item in callback_metadata if item.get('Name') == 'MpesaReceiptNumber'), None)
                        amount = next((item.get('Value') for item in callback_metadata if item.get('Name') == 'Amount'), None)
                        transaction_date_str = next((item.get('Value') for item in callback_metadata if item.get('Name') == 'TransactionDate'), None)
                        
                        transaction_date = None
                        if transaction_date_str:
                            transaction_date = datetime.strptime(str(transaction_date_str), '%Y%m%d%H%M%S')

                        # updating transaction fields
                        transaction.mpesa_receipt_number = receipt_number
                        transaction.transaction_date = transaction_date
                        transaction.amount = amount
                        transaction.status = "Success"
                        transaction.description = "Payment Successful"
                        transaction.save()
                        
                        ## SEND EMAIL
                        if transaction.email:
                            subject = "Payment Receipt Confirmation"
                            message = (
                                f"Dear {transaction.name}, \n\n"
                                f"Thank you for your payment of {transaction.amount}\n"
                                f"Your MPESA confirmation receipt is {transaction.mpesa_receipt_number}\n"
                                "Best Regards , \n"
                                "STK PUSH"
                            )
                            html_message = (
                                f"<p>Dear {transaction.name},</p>"
                                f"<p>Thank you for your payment of {transaction.amount}</p>"
                                f"<p>Your MPESA confirmation receipt is {transaction.mpesa_receipt_number}</p>"
                                f"<p>Best Regards, STK Push</p>"
                            )
                            send_mail(subject,message,'kengereomuri@gmail.com',[transaction.email],
                                      fail_silently=False,html_message=html_message,)

                    elif result_code == 1: # Failure
                        transaction.status = "Failed"
                        transaction.description = result_desc
                        transaction.save()

                    elif result_code == 1032: # Cancellation
                        transaction.status = "Cancelled"
                        transaction.description = "Transaction Cancelled by User"
                        transaction.save()

            return JsonResponse({"message": "callback received and processed"}, status=200)

        except Exception as e:
            print(f"Error processing callback {e}")
            return JsonResponse({"error": f"Error processing callback {e}"}, status=500)

    return JsonResponse({"error" : "Invalid request method"}, status=400)


def check_status(request, transaction_id):
    transaction = Transactions.objects.filter(id=transaction_id).first()
    if not transaction:
        return JsonResponse({"status": "failed" , "message": "Transaction not found"}, status=400)

    if transaction.status == "Success":
        return JsonResponse({"status": "Success", "message": "Payment Successful"}, status=200)
    elif transaction.status == "Failed":
        return JsonResponse({"status": "Failed", "message": "Payment Failed"}, status=200)
    elif transaction.status == "Cancelled":
        return JsonResponse({"status": "Cancelled", "message": "Transaction was Cancelled"}, status=200)
    else:
        return JsonResponse({"status": "Pending", "message": "Transaction still being processed."}, status=400)


def payment_success(request):
    return render(request,"invoices/payment_success.html")

def payment_failed(request):
    return render(request,"invoices/payment_failed.html")

def payment_cancelled(request):
    return render(request,"invoices/payment_cancelled.html")


# -----------------------------------------------
# INVOICE CRUD VIEWS
# -----------------------------------------------

# 1. Invoice List View (for issued and received)
class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'invoices/invoice_list.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        user = self.request.user
        # Show all invoices where the user is either the freelancer (issued) or the client (received)
        # Using Q objects or | (OR) is efficient for this type of query
        return Invoice.objects.filter(freelancer=user) | Invoice.objects.filter(client=user)
    
# 2. Invoice Detail View
class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'invoices/invoice_detail.html'
    context_object_name = 'invoice'

    def get_queryset(self):
        # Ensure only the freelancer or client can view the invoice
        user = self.request.user
        # Filter by PK AND (freelancer=user OR client=user)
        return Invoice.objects.filter(pk=self.kwargs['pk']).filter(
            freelancer=user
        ) | Invoice.objects.filter(pk=self.kwargs['pk']).filter(
            client=user
        )

# 3. Invoice Create View (Handles nested items using formsets)
def invoice_create_view(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST) # Formset handles validation and data for items
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # Save the main Invoice object first
                invoice = form.save(commit=False)
                # Set the freelancer to the currently logged-in user
                invoice.freelancer = request.user 
                invoice.save()
                
                # Link the items to the saved invoice and save them
                # Note: The formset will automatically link items via the ForeignKey when saved
                formset.instance = invoice 
                formset.save()
                
                # The totals (subtotal, total_amount) are calculated and saved 
                # automatically by the InvoiceItem model's save method, which triggers
                # the parent invoice's calculate_totals method.
                
                return redirect('invoices:invoice_detail', pk=invoice.pk)
    else:
        # GET request: instantiate blank forms
        form = InvoiceForm()
        # Initialize formset with a new Invoice instance for the foreign key context
        formset = InvoiceItemFormSet(instance=Invoice()) 
        
    return render(request, 'invoices/invoice_create.html', {
        'form': form, 
        'formset': formset
    })

# DELETED: The InvoiceCreateView class stub is removed as the function-based view is used.