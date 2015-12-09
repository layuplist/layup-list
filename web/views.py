from django.shortcuts import render
from web.models import Course
from django.conf import settings

LIMIT = 100

def current_term(request):

    sort = request.GET.get("sort")
    if sort == "quality":
        course_type = "Good Classes"
        primary_sort = "-quality_score"
        secondary_sort = "-layup_score"
    else:
        course_type = "Layups"
        primary_sort = "-layup_score"
        secondary_sort = "-quality_score"

    return render(request, 'current_term.html', {
        'term': settings.CURRENT_TERM,
        'course_type': course_type,
        'count': Course.objects.for_term(settings.CURRENT_TERM).count(),
        'courses': Course.objects.for_term(settings.CURRENT_TERM).prefetch_related(
            'distribs'
        ).order_by(primary_sort, secondary_sort)[:LIMIT],
        'page_javascript': 'LayupList.Web.CurrentTerm()'
    })
