"""
ASGI server wrapper for Django Retrace Lost & Found application
This allows the Django app to be served via uvicorn as required by supervisor
"""
import os
import sys
from pathlib import Path

# Add parent directory to Python path so we can import the Django project
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Retrace.settings')

# Import Django's ASGI application
from django.core.asgi import get_asgi_application

# Create the ASGI application
app = get_asgi_application()
