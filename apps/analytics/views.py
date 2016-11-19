from django.shortcuts import render
from django.views.decorators.http import require_safe
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponseBadRequest
from apps.web import models
from apps.analytics.forms import ManualSentimentForm
from apps.recommendations.models import Recommendation
from lib import constants
from collections import Counter
import datetime
import pytz
from random import randint

LIMIT = 15


@require_safe
@staff_member_required
def home(request):
    course_picker = User.objects.get(username='CoursePicker')

    non_zero_votes = models.Vote.objects.exclude(value=0)
    num_voters = non_zero_votes.values_list('user').distinct().count()
    num_quality_voters = non_zero_votes.filter(
        category=models.Vote.CATEGORIES.QUALITY).values_list(
        'user').distinct().count()
    num_layup_voters = non_zero_votes.filter(
        category=models.Vote.CATEGORIES.DIFFICULTY).values_list(
        'user').distinct().count()
    num_reviewers = models.Review.objects.exclude(
        user=course_picker).values_list('user').distinct().count()

    now = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    month_ago = ('Month', now - datetime.timedelta(days=31))
    week_ago = ('Week', now - datetime.timedelta(weeks=1))
    today = ('Today', now - datetime.timedelta(hours=24))

    overall_table = [(
        'Total',
        User.objects.count(),
        models.Vote.objects.exclude(value=0).filter(
            category=models.Vote.CATEGORIES.QUALITY).count(),
        models.Vote.objects.exclude(value=0).filter(
            category=models.Vote.CATEGORIES.DIFFICULTY).count(),
        "{} ({} exclusive)".format(
            models.Review.objects.count(),
            models.Review.objects.exclude(user=course_picker).count()),
    )]
    for name, earliest_date in [month_ago, week_ago, today]:
        non_zero_votes_since = non_zero_votes.filter(
            created_at__gte=earliest_date)
        overall_table.append((
            name,
            User.objects.filter(date_joined__gte=earliest_date).count(),
            non_zero_votes_since.filter(
                category=models.Vote.CATEGORIES.QUALITY).count(),
            non_zero_votes_since.filter(
                category=models.Vote.CATEGORIES.DIFFICULTY).count(),
            models.Review.objects.filter(
                created_at__gte=earliest_date).count(),
        ))

    vote_table = [(
        'Total',
        models.Vote.objects.filter(
            value__gt=0, category=models.Vote.CATEGORIES.QUALITY).count(),
        models.Vote.objects.filter(
            value__lt=0, category=models.Vote.CATEGORIES.QUALITY).count(),
        models.Vote.objects.filter(
            value__gt=0, category=models.Vote.CATEGORIES.DIFFICULTY).count(),
        models.Vote.objects.filter(
            value__lt=0, category=models.Vote.CATEGORIES.DIFFICULTY).count(),
        models.Vote.objects.filter(value=0).count(),
    )]
    for name, earliest_date in [month_ago, week_ago, today]:
        vote_table.append((
            name,
            models.Vote.objects.filter(
                value__gt=0,
                category=models.Vote.CATEGORIES.QUALITY,
                created_at__gte=earliest_date).count(),
            models.Vote.objects.filter(
                value__lt=0,
                category=models.Vote.CATEGORIES.QUALITY,
                created_at__gte=earliest_date).count(),
            models.Vote.objects.filter(
                value__gt=0,
                category=models.Vote.CATEGORIES.DIFFICULTY,
                created_at__gte=earliest_date).count(),
            models.Vote.objects.filter(
                value__lt=0,
                category=models.Vote.CATEGORIES.DIFFICULTY,
                created_at__gte=earliest_date).count(),
            models.Vote.objects.filter(
                value=0,
                created_at__gte=earliest_date).count(),
        ))

    usernames = User.objects.exclude(
        id=course_picker.id).values_list('username', flat=True)
    c = Counter()
    for username in usernames:
        year_string = username.split('.')[-1]
        c[year_string] += 1
    class_breakdown = sorted(
        [(year, count,) for year, count in c.items() if len(year) == 2]
    )

    recommendations_last_updated = []
    for creator, description in Recommendation.CREATORS:
        rec = Recommendation.objects.filter(
            creator=creator).order_by('created_at')[:1]
        if rec:
            recommendations_last_updated.append((
                description, rec[0].created_at))
        else:
            recommendations_last_updated.append((
                description, "never"))

    return render(request, 'dashboard.html', {
        'overall_table': overall_table,
        'vote_table': vote_table,

        'num_voters': num_voters,
        'num_quality_voters': num_quality_voters,
        'num_layup_voters': num_layup_voters,
        'num_reviewers': num_reviewers,

        'recommendations_last_updated': recommendations_last_updated,

        'activated_accounts': User.objects.filter(is_active=True).count(),

        'class_breakdown': class_breakdown,
    })


@require_safe
@staff_member_required
@user_passes_test(lambda u: u.is_superuser)
def eligible_for_recommendations(request):
    eligible_users_and_votes = (
        models.Vote.objects
        .filter(value=1, category=models.Vote.CATEGORIES.QUALITY)
        .values_list('user')
        .annotate(vote_count=Count('user'))
        .filter(vote_count__gte=constants.REC_UPVOTE_REQ)
        .order_by('-vote_count')
        .values_list('user__username', 'user', 'vote_count'))
    return render(request, 'eligible_for_recommendations.html', {
        'users_and_votes': eligible_users_and_votes
    })


@staff_member_required
@user_passes_test(lambda u: u.is_superuser)
def sentiment_labeler(request):
    if request.method == 'POST':
        form = ManualSentimentForm(request.POST)
        if form.is_valid():
            form.save_sentiment()
        else:
            return render(request, 'sentiment_labeler.html', {
                'review': models.Review.objects.get(id=form.review_id),
                'form': form,
            })
    unlabeled_reviews = models.Review.objects.filter(
        user=User.objects.get(username="CoursePicker"),
    ).exclude(
        sentiment_labeler=models.Review.MANUAL_SENTIMENT_LABELER,
    )
    count = unlabeled_reviews.count()
    random_index = randint(0, count - 1)
    review = unlabeled_reviews[random_index]
    form = ManualSentimentForm(initial={'review_id': review.id})
    return render(request, 'sentiment_labeler.html', {
        'count': count,
        'labeled_count': models.Review.objects.filter(
            sentiment_labeler=models.Review.MANUAL_SENTIMENT_LABELER).count(),
        'form': form,
        'review': review,
    })
