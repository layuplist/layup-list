from django.shortcuts import render
from web.models import Course, CourseMedian
from django.conf import settings

LIMIT = 20


def current_term(request):
    print request

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


def course_detail(request, course_id):
    course = Course.objects.get(pk=course_id)
    return render(request, 'course_detail.html', {
        'course': course,
        'medians': course.coursemedian_set.all(),
        'reviews': course.review_set.all(),
        'page_javascript': 'LayupList.Web.CourseDetail()'
    })


def search(request, query):
    info = query.split()

    try:
        department = info[0]
    except IndexError:
        department = ""

    try:
        number = info[1]
    except IndexError:
        number = None

    try:
        name = info[2]
    except IndexError:
        name = ""

    courses = Course.objects.filter(
        department=department,
        number=number,
        # title__like=name
    )

    if not courses:
        return
    else:
        return render(request, 'search.html', {
            'courses': courses,
            'page_javascript': 'LayupList.Web.Search()'
        })
