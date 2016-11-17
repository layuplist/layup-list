from datetime import datetime, timedelta
from celery import shared_task

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import get_template
from django.template import Context

from web.models import Review, Vote
from lib import constants, task_utils


@shared_task
@task_utils.email_if_fails
def send_analytics_email_update(lookback=timedelta(days=7)):
    context = _get_analytics_email_context(lookback)
    content = get_template('analytics_email.txt').render(Context(context))
    send_mail(
        'Layup List Weekly Update',
        content,
        constants.SUPPORT_EMAIL,
        [email for _, email in settings.ADMINS],
        fail_silently=False,
    )


def _get_analytics_email_context(lookback):
    changes_since = datetime.now() - lookback
    new_query = Q(created_at__gte=changes_since)
    users = User.objects.all()
    good_votes = Vote.objects.filter(category=Vote.CATEGORIES.GOOD)
    good_upvotes = good_votes.filter(value=1)
    good_downvotes = good_votes.filter(value=-1)
    layup_votes = Vote.objects.filter(category=Vote.CATEGORIES.LAYUP)
    layup_upvotes = layup_votes.filter(value=1)
    layup_downvotes = layup_votes.filter(value=-1)
    return {
        'users': {
            'all': users,
            'new': users.filter(date_joined__gte=changes_since),
            'unique_recent_logins': users.filter(
                last_login__gte=changes_since),
        },
        'votes': {
            'all_good_upvotes': good_upvotes,
            'all_good_downvotes': good_downvotes,
            'all_layup_upvotes': layup_upvotes,
            'all_layup_downvotes': layup_downvotes,
            'new_good_upvotes': good_upvotes.filter(new_query),
            'new_good_downvotes': good_downvotes.filter(new_query),
            'new_layup_upvotes': layup_upvotes.filter(new_query),
            'new_layup_downvotes': layup_downvotes.filter(new_query),
        },
        'reviews': {
            'all': Review.objects.all(),
            'new': Review.objects.filter(new_query),
        },
    }
