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
        'task': 'apps.analytics.tasks.send_analytics_email_update',
        'schedule': crontab(minute=0, hour=0, day_of_week=1),  # Mon, 12AM
    },
    'course_description_similarity': {
        'task': (
            'apps.recommendations.tasks.'
            'generate_course_description_similarity_recommendations'),
        'schedule': crontab(hour=0, minute=0, day_of_week=2),  # Tues, 12AM
    },
    'crawl_orc': {
        'task': 'apps.spider.tasks.crawl_orc',
        'schedule': crontab(minute=0, hour=1),  # 1AM
    },
    'crawl_timetable': {
        'task': 'apps.spider.tasks.crawl_timetable',
        'schedule': crontab(minute=30, hour=1),  # 1:30AM
    },
    'crawl_medians': {
        'task': 'apps.spider.tasks.crawl_medians',
        'schedule': crontab(minute=0, hour=2),  # 2AM
    },
    'request_term_change': {
        'task': 'apps.analytics.tasks.possibly_request_term_update',
        'schedule': crontab(minute=0, hour=3),  # 3AM
    },
}
