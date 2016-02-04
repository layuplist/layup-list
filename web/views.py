from django.shortcuts import render, redirect
from web.models import Course, CourseMedian, Student
from django.conf import settings
from django.views.decorators.http import require_safe
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from lib.grades import numeric_value_for_grade
from lib.terms import numeric_value_of_term
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
import sys
from lib import constants

LIMITS = {
    "courses": 20,
    "reviews": 5,
}


@require_safe
def landing(request):
    return render(request, 'landing.html', {"landing": True})


def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not Student.objects.is_valid_dartmouth_student_email(email):
            return render(request, 'signup.html', {
                "error": """
                    Only Dartmouth student emails are permitted for
                    registration at this time. Contact us at
                    support@layuplist.com for more information.
                """
            })

        try:
            with transaction.atomic():
                new_user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    is_active=False
                )

                new_student = Student.objects.create(
                    user=new_user,
                    confirmation_link=User.objects.make_random_password(length=16)
                )

                new_student.send_confirmation_link(request)

                return render(request, 'instructions.html')

        except IntegrityError:
            return render(request, 'signup.html', { "error": "This email is already registered. If you believe this is a mistake, please email support@layuplist.com."})

    elif request.method == 'GET':
        return render(request, 'signup.html')

    else:
        return render(request, 'signup.html', { "error": "Improper request type."})


def auth_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.GET.get('next', '/layups')

        user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(next_url)
            else:
                return render(request, 'login.html', { "inactive": True, "error": "Please activate your account via the activation link first."})
        else:
            return render(request, 'login.html', { "error": "Invalid login."})

    elif request.method == 'GET':
        return render(request, 'login.html')

    else:
        return render(request, 'login.html', {
            "error": "Please authenticate."
        })


@login_required
def auth_logout(request):
    logout(request)
    return render(request, 'logout.html')


@require_safe
def confirmation(request):
    link = request.GET.get('link')

    if link:
        try:
            student = Student.objects.get(confirmation_link=link)
        except Student.DoesNotExist:
            return render(request, 'confirmation.html', {
                'error': 'Confirmation code expired or does not exist.'
            })

        if student.user.is_active:
            return render(request, 'confirmation.html', { 'already_confirmed': True})

        student.user.is_active = True
        student.user.save()
        return render(request, 'confirmation.html', { 'already_confirmed': False})


@require_safe
def landing(request):
    return render(request, 'landing.html')


@require_safe
def current_term(request, sort):
    if sort == "best":
        course_type, primary_sort, secondary_sort = "Best Classes", "-quality_score", "-layup_score"
    else:
        course_type, primary_sort, secondary_sort = "Layups", "-layup_score", "-quality_score"

    term_courses = Course.objects.for_term(constants.CURRENT_TERM).prefetch_related(
        'distribs', 'review_set', 'courseoffering_set'
    ).order_by(primary_sort, secondary_sort)

    paginator = Paginator(term_courses, LIMITS["courses"])
    try:
        courses = paginator.page(request.GET.get('page'))
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)

    return render(request, 'current_term.html', {
        'term': constants.CURRENT_TERM,
        'sort': sort,
        'course_type': course_type,
        'courses': courses,
        'page_javascript': 'LayupList.Web.CurrentTerm()'
    })


@require_safe
@login_required
def course_detail(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    paginator = Paginator(course.review_set.all().order_by("-term"), LIMITS["reviews"])
    try:
        reviews = paginator.page(request.GET.get('page'))
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    return render(request, 'course_detail.html', {
        'term': constants.CURRENT_TERM,
        'course': course,
        'reviews': reviews,
        'distribs': course.distribs_string(),
        'xlist': course.crosslisted_courses.all(),
        'page_javascript': 'LayupList.Web.CourseDetail({})'.format(course_id)
    })


@require_safe
def course_search(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 3:
        return render(request, 'course_search.html', {
            'query': query,
            'courses': []
        })
    courses = Course.objects.search(query).prefetch_related('review_set')
    if len(courses) == 1:
        return redirect(courses[0])

    if len(query) not in Course.objects.DEPARTMENT_LENGTHS:
        courses = sorted(courses, key=lambda c: c.review_set.count(), reverse=True)

    return render(request, 'course_search.html', {
        'query': query,
        'courses': courses
    })


@require_safe
def course_review_search(request, course_id):
    query = request.GET.get("q", "").strip()
    course = Course.objects.get(id=course_id)
    return render(request, 'course_review_search.html', {
        'query': query,
        'course': course,
        'reviews': course.search_reviews(query),
        'page_javascript': 'LayupList.Web.CourseReviewSearch()'
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
