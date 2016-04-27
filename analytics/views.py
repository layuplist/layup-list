from django.shortcuts import render
from django.views.decorators.http import require_safe
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count
from web import models
from collections import Counter
import datetime

LIMIT = 50


@require_safe
@staff_member_required
def home(request):
    course_picker = User.objects.get(username='CoursePicker')

    high_voters = models.Vote.objects.exclude(value=0).values_list('user').annotate(
        vote_count=Count('user')).order_by('-vote_count').values_list('user', 'vote_count')[:LIMIT]
    high_good_voters = models.Vote.objects.exclude(value=0).filter(category=models.Vote.CATEGORIES.GOOD).values_list('user').annotate(
        vote_count=Count('user')).order_by('-vote_count').values_list('user', 'vote_count')[:LIMIT]
    high_layup_voters = models.Vote.objects.exclude(value=0).filter(category=models.Vote.CATEGORIES.LAYUP).values_list('user').annotate(
        vote_count=Count('user')).order_by('-vote_count').values_list('user', 'vote_count')[:LIMIT]
    top_reviewers = models.Review.objects.exclude(user=course_picker).values_list('user').annotate(review_count=Count('user')).order_by('-review_count').values_list('user', 'review_count')[:LIMIT]

    now = datetime.datetime.now()
    month_ago = ('Month', now - datetime.timedelta(days=31))
    week_ago = ('Week', now - datetime.timedelta(weeks=1))
    today = ('Today', datetime.date.today())

    overall_table = [(
        'Total',
        User.objects.count(),
        models.Vote.objects.exclude(value=0).filter(category=models.Vote.CATEGORIES.GOOD).count(),
        models.Vote.objects.exclude(value=0).filter(category=models.Vote.CATEGORIES.LAYUP).count(),
        "{} ({} exclusive)".format(models.Review.objects.count(), models.Review.objects.exclude(user=course_picker).count()),
    )]
    for name, earliest_date in [month_ago, week_ago, today]:
        overall_table.append((
            name,
            User.objects.filter(date_joined__gte=earliest_date).count(),
            models.Vote.objects.exclude(value=0).filter(created_at__gte=earliest_date, category=models.Vote.CATEGORIES.GOOD).count(),
            models.Vote.objects.exclude(value=0).filter(created_at__gte=earliest_date, category=models.Vote.CATEGORIES.LAYUP).count(),
            models.Review.objects.filter(created_at__gte=earliest_date).count(),
        ))

    vote_table = [(
        'Total',
        models.Vote.objects.filter(value__gt=0, category=models.Vote.CATEGORIES.GOOD).count(),
        models.Vote.objects.filter(value__lt=0, category=models.Vote.CATEGORIES.GOOD).count(),
        models.Vote.objects.filter(value__gt=0, category=models.Vote.CATEGORIES.LAYUP).count(),
        models.Vote.objects.filter(value__lt=0, category=models.Vote.CATEGORIES.LAYUP).count(),
        models.Vote.objects.filter(value=0).count(),
    )]
    for name, earliest_date in [month_ago, week_ago, today]:
        vote_table.append((
            name,
            models.Vote.objects.filter(value__gt=0, category=models.Vote.CATEGORIES.GOOD, created_at__gte=earliest_date).count(),
            models.Vote.objects.filter(value__lt=0, category=models.Vote.CATEGORIES.GOOD, created_at__gte=earliest_date).count(),
            models.Vote.objects.filter(value__gt=0, category=models.Vote.CATEGORIES.LAYUP, created_at__gte=earliest_date).count(),
            models.Vote.objects.filter(value__lt=0, category=models.Vote.CATEGORIES.LAYUP, created_at__gte=earliest_date).count(),
            models.Vote.objects.filter(value=0, created_at__gte=earliest_date).count(),
        ))

    usernames = User.objects.exclude(id=course_picker.id).values_list('username', flat=True)
    c = Counter()
    for username in usernames:
        year_string = username.split('.')[-1]
        c[year_string] += 1
    class_breakdown = sorted(
        [(year, count,) for year, count in c.items() if len(year) == 2]
    )

    return render(request, 'home.html', {
        'overall_table': overall_table,
        'vote_table': vote_table,

        'high_voters': high_voters,
        'high_good_voters': high_good_voters,
        'high_layup_voters': high_layup_voters,
        'top_reviewers': top_reviewers,

        'class_breakdown': class_breakdown,
    })
