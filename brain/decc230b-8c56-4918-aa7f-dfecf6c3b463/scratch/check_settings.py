import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uphirex.settings')
django.setup()

from django.conf import settings

print(f"ADZUNA_APP_ID: '{settings.ADZUNA_APP_ID}'")
print(f"ADZUNA_APP_KEY: '{settings.ADZUNA_APP_KEY}'")
