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
from django.db import IntegrityError
import sys
from lib import constants

LIMITS = {
    "courses": 20,
    "reviews": 5,
}

VALID_STUDENT = set(['16', '17', '18', '19', '20'])


@require_safe
def landing(request):
    return render(request, 'landing.html', {})


def confirm_dartmouth_student_email(email):

    e = email.split("@")
    dnd_name = e[0]
    domain = e[1] # will be 'alumni' for alumni emails
    if domain != "dartmouth.edu":
        return False

    dnd_parts = dnd_name.split('.')

    if dnd_parts[-1] not in VALID_STUDENT: # dnd student names end in number
        return False

    return True



def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not confirm_dartmouth_student_email(email):
            return render(request, 'signup.html', {"error": "Only Dartmouth student emails are permitted for registration at this time. Contact us at support@layuplist.com for more information."})

        link = User.objects.make_random_password(length=16, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        
        try:
            new_user = User.objects.create_user(username=email, email=email, password=password, is_active=False)
        except IntegrityError:
            return render(request, 'signup.html', {"error": "This email is already registered. If you believe this is a mistake, please email support@layuplist.com."})

        new_student = Student.objects.create(user=new_user, confirmation_link=link)

        full_link = request.META['HTTP_HOST'] + '/confirmation?link=' + link
        print full_link # remove on prod
        sys.stdout.flush() # pythonunbuffered

        return render(request, 'instructions.html', {})

    elif request.method == 'GET':
        return render(request, 'signup.html', {})

    else:
        return render(request, 'signup.html', {"error": "Improper request type."})


def auth_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email and password:
            user = authenticate(username=email, password=password)

            if user.is_active:
                login(request, user)
                return redirect('/current_term')

            else:
                return render(request, 'login.html', {"error": "This account is not active."})

        else:
            return render(request, 'login.html', {"error": "Must provide both email and password."})

    elif request.method == 'GET':
        return render(request, 'login.html', {})

    else:
        return render(request, 'login.html', {"error": "Please authenticate."})

@login_required
def auth_logout(request):
    logout(request)
    return render(request, 'logout.html', {})


@require_safe
def confirmation(request):
    link = request.GET.get('link')

    if link:
        student = Student.objects.get(confirmation_link=link)

        if student.user.is_active:
            return render(request, 'confirmation.html', {'already_confirmed': True})

        # print "is not active!"
        student.user.is_active = True
        student.user.save()
        return render(request, 'confirmation.html', {'already_confirmed': False})


@require_safe
def current_term(request):
    if request.GET.get("sort") == "quality":
        course_type, primary_sort, secondary_sort = "Good Classes", "-quality_score", "-layup_score"
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

    paginator = Paginator(course.review_set.all().order_by("-created_at"), LIMITS["reviews"])
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
def search(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 3:
        return render(request, 'search.html', {
            'query': query,
            'courses': []
        })
    courses = Course.objects.search(query).prefetch_related('review_set')
    if len(courses) == 1:
        return redirect(courses[0])

    if len(query) not in Course.objects.DEPARTMENT_LENGTHS:
        courses = sorted(courses, key=lambda c: c.review_set.count(), reverse=True)

    return render(request, 'search.html', {
        'query': query,
        'courses': courses
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
