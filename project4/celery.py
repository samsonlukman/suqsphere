from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project4.settings')

app = Celery('project4')

app.config_from_object('django.conf:settings', namespace='CELERY')

# ✅ Explicitly tell Celery where to find tasks
app.autodiscover_tasks([
    'network',
    'network.notifications',
])

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

