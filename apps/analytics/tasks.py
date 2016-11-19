from datetime import datetime, timedelta
from celery import shared_task

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import get_template
from django.template import Context

from apps.web.models import CourseOffering, Review, Vote
from lib import constants, task_utils, terms


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
    quality_votes = Vote.objects.filter(category=Vote.CATEGORIES.QUALITY)
    quality_upvotes = quality_votes.filter(value=1)
    quality_downvotes = quality_votes.filter(value=-1)
    difficulty_votes = Vote.objects.filter(category=Vote.CATEGORIES.DIFFICULTY)
    difficulty_upvotes = difficulty_votes.filter(value=1)
    difficulty_downvotes = difficulty_votes.filter(value=-1)
    return {
        'users': {
            'all': users,
            'new': users.filter(date_joined__gte=changes_since),
            'unique_recent_logins': users.filter(
                last_login__gte=changes_since),
        },
        'votes': {
            'all_quality_upvotes': quality_upvotes,
            'all_quality_downvotes': quality_downvotes,
            'all_difficulty_upvotes': difficulty_upvotes,
            'all_difficulty_downvotes': difficulty_downvotes,
            'new_quality_upvotes': quality_upvotes.filter(new_query),
            'new_quality_downvotes': quality_downvotes.filter(new_query),
            'new_difficulty_upvotes': difficulty_upvotes.filter(new_query),
            'new_difficulty_downvotes': difficulty_downvotes.filter(new_query),
        },
        'reviews': {
            'all': Review.objects.all(),
            'new': Review.objects.filter(new_query),
        },
    }


@shared_task
@task_utils.email_if_fails
def possibly_request_term_update():
    next_term = terms.get_next_term(constants.CURRENT_TERM)
    next_term_count = CourseOffering.objects.filter(term=next_term).count()
    if next_term_count:
        send_mail(
            'Term may be out of date ({} offerings with term {})'.format(
                next_term_count, next_term),
            'Consider modifying the environment variable.',
            constants.SUPPORT_EMAIL,
            [email for _, email in settings.ADMINS],
            fail_silently=False,
        )
    return next_term_count
