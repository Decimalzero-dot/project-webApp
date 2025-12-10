import os
import sys
import django
import traceback
from pathlib import Path

# Ensure project root is on sys.path so Django settings can be imported
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FREELANCE.settings')

django.setup()

from django.core.mail import send_mail

from django.conf import settings
from django.core.mail import get_connection

print('EMAIL_BACKEND from settings:', getattr(settings, 'EMAIL_BACKEND', None))
print('EMAIL_HOST:', getattr(settings, 'EMAIL_HOST', None))
print('EMAIL_PORT:', getattr(settings, 'EMAIL_PORT', None))
print('EMAIL_USE_TLS:', getattr(settings, 'EMAIL_USE_TLS', None))
print('EMAIL_HOST_USER:', getattr(settings, 'EMAIL_HOST_USER', None))

from_email = os.environ.get('DEFAULT_FROM_EMAIL') or os.environ.get('EMAIL_HOST_USER')
recipient = os.environ.get('EMAIL_HOST_USER')

try:
    # show connection details
    conn = get_connection()
    print('Email backend class:', conn.__class__)
except Exception as e:
    print('Could not create email connection:', e)
    conn = None

try:
    sent = send_mail(
        'Dev Test Email (script)',
        'This is a test sent from the local dev environment to verify SMTP settings.',
        from_email,
        [recipient],
        fail_silently=False,
    )
    print('send_mail returned:', sent)
except Exception as e:
    print('Exception occurred:')
    traceback.print_exc()
