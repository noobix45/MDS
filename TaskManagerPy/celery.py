# TaskManagerPy/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Setează modulul de settings pentru Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TaskManagerPy.settings')

app = Celery('TaskManagerPy')

# Folosește setările din Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Încarcă task-urile din toate aplicațiile înregistrate
app.autodiscover_tasks()

# Setări pentru a rula periodic task-ul
app.conf.beat_schedule = {
    'trimite-notificari': {
        'task': 'task_manager.tasks.trimite_notificari_periodic',
        'schedule': crontab(minute='*/3'),  #la 3 minute
    },
}