import os
import smtplib
import sys
from pathlib import Path

# Add project root so settings import works
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FREELANCE.settings')
import django
django.setup()
from django.conf import settings

host = getattr(settings, 'EMAIL_HOST', None)
port = getattr(settings, 'EMAIL_PORT', None)
user = getattr(settings, 'EMAIL_HOST_USER', None)
password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
use_tls = getattr(settings, 'EMAIL_USE_TLS', None)

print('Connecting to', host, port)
try:
    server = smtplib.SMTP(host, port, timeout=10)
    server.set_debuglevel(1)
    server.ehlo()
    if use_tls:
        print('Starting TLS')
        server.starttls()
        server.ehlo()
    print('Attempting login for user:', user)
    server.login(user, password)
    print('Login successful')
    server.quit()
except Exception as e:
    print('SMTP exception:')
    import traceback; traceback.print_exc()
