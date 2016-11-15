from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'layup_list.settings')
app = Celery('layup_list')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'weekly_analytics_update': {
        'task': 'analytics.tasks.send_analytics_email_update',
        'schedule': crontab(hour=0),  # Midnight
    },
}
