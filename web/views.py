from django.shortcuts import render, redirect
from web.models import Course, CourseMedian
from django.conf import settings
from django.views.decorators.http import require_safe
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

LIMITS = {
    "courses": 20,
    "reviews": 8,
}

@require_safe
def current_term(request):
    if request.GET.get("sort") == "quality":
        course_type, primary_sort, secondary_sort = "Good Classes", "-quality_score", "-layup_score"
    else:
        course_type, primary_sort, secondary_sort = "Layups", "-layup_score", "-quality_score"

    term_courses = Course.objects.for_term(settings.CURRENT_TERM).prefetch_related('distribs').order_by(primary_sort, secondary_sort)

    paginator = Paginator(term_courses, LIMITS["courses"])
    try:
        courses = paginator.page(request.GET.get('page'))
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)

    return render(request, 'current_term.html', {
        'term': settings.CURRENT_TERM,
        'course_type': course_type,
        'courses': courses,
        'page_javascript': 'LayupList.Web.CurrentTerm()'
    })


@require_safe
def course_detail(request, course_id):
    course = Course.objects.get(pk=course_id)

    paginator = Paginator(course.review_set.all().order_by("-created_at"), LIMITS["reviews"])
    try:
        reviews = paginator.page(request.GET.get('page'))
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    return render(request, 'course_detail.html', {
        'course': course,
        'medians': course.coursemedian_set.all(),
        'reviews': reviews,
        'page_javascript': 'LayupList.Web.CourseDetail()'
    })


@require_safe
def search(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 3:
        return render(request, 'search.html', {
            'query': query,
            'courses': []
        })
    courses = Course.objects.search(query).prefetch_related('distribs')

    if len(courses) == 1:
        return redirect(courses[0])

    return render(request, 'search.html', {
        'query': query,
        'courses': courses,
    })
