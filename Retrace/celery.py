<<<<<<< HEAD
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Retrace.settings')
app = Celery('Retrace')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
=======
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Retrace.settings')
app = Celery('Retrace')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
>>>>>>> 8b1e1d938e70917f9e7bc0a124a56dd9f9496b7e
