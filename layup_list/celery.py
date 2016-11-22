from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'layup_list.settings')
app = Celery('layup_list')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'analytics_update': {
        'task': 'analytics.tasks.send_analytics_email_update',
        'schedule': crontab(minute=0, hour=0),  # Midnight
    },
    'course_description_similarity': {
        'task': (
            'recommendations.tasks.'
            'generate_course_description_similarity_recommendations'),
        'schedule': crontab(hour=0, minute=0, day_of_week=2),  # Tues, 12AM
    },
    'crawl_orc': {
        'task': 'spider.tasks.crawl_orc',
        'schedule': crontab(minute=0, hour=1),  # 1AM
    },
    'crawl_medians': {
        'task': 'spider.tasks.crawl_medians',
        'schedule': crontab(minute=0, hour=2),  # 2AM
    },
}
