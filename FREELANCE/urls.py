# FREELANCE/urls.py - The final, correct version

from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views # Import module to access views like welcome_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ROOT PATH: Directs unauthorized users to the welcome landing page.
    # The view handles redirecting authenticated users to their respective dashboards.
    path('', accounts_views.welcome_view, name='homepage'), 
    
    # App URLs
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('clients/', include(('clients.urls', 'clients'), namespace='clients')),
    path('freelancers/', include(('freelancers.urls', 'freelancers'), namespace='freelancers')),
    path('tasks/', include(('tasks.urls', 'tasks'), namespace='tasks')),
    path('invoices/', include('invoices.urls', namespace='invoices')),
]