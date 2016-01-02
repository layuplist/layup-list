from django.shortcuts import render, redirect
from web.models import Course, CourseMedian
from django.conf import settings
from django.views.decorators.http import require_safe
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from lib.grades import numeric_value_for_grade
from lib.terms import numeric_value_of_term

LIMITS = {
    "courses": 20,
    "reviews": 8,
}

@require_safe
def landing(request):
    return render(request, 'landing.html', {})

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
        'reviews': reviews,
        'page_javascript': 'LayupList.Web.CourseDetail({})'.format(course_id)
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

@require_safe
def medians(request, course_id):

    # retrieve course medians for term, and group by term for averaging
    medians_by_term = {}
    for course_median in CourseMedian.objects.filter(course=course_id):
        if course_median.term not in medians_by_term:
            medians_by_term[course_median.term] = []

        medians_by_term[course_median.term].append({
            'median': course_median.median,
            'enrollment': course_median.enrollment,
            'section': course_median.section,
            'numeric_value': numeric_value_for_grade(course_median.median)
        })

    return JsonResponse({ 'medians': sorted(
        [
            {
            'term': term,
            'avg_numeric_value': sum([m['numeric_value'] for m in term_medians]) / len(term_medians),
            'courses': term_medians,
            } for term, term_medians in medians_by_term.iteritems()
        ],
        key=lambda x: numeric_value_of_term(x['term']),
        reverse=True
    )})
