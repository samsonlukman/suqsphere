# project4/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project4.settings')

app = Celery('project4')

# Configure broker and backend
app.conf.update(
    broker_url='django-db://',
    result_backend='django-db',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')