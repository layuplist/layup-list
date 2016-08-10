"""layup_list URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
import django.contrib.auth.views as authviews
from web import views
from analytics import views as aviews
from recommendations import views as rviews

urlpatterns = [

    # administrative
    url(r'^admin/', admin.site.urls),
    url(r'^hijack/', include('hijack.urls')),

    # analytics
    url(r'^analytics/$', aviews.home, name='analytics_home'),
    url(r'^eligible_for_recommendations/$', aviews.eligible_for_recommendations, name='eligible_for_recommendations'),

    # primary views
    url(r'^$', views.landing, name="landing"),
    url(r'^(?P<sort>best|layups)/?', views.current_term, name="current_term"),
    url(r'^search/?', views.course_search, name="course_search"),
    url(r'^course/(?P<course_id>[0-9]+)$',
        views.course_detail, name="course_detail"),
    url(r'^course/(?P<course_id>[0-9]+)/review_search/?',
        views.course_review_search, name="course_review_search"),

    # recommendations
    url(r'^recommendations/?', rviews.recommendations, name='recommendations'),

    # api
    url(r'^api/course/(?P<course_id>[0-9].*)/medians',
        views.medians, name="medians"),
    url(r'^api/course/(?P<course_id>[0-9].*)/professors?/?',
        views.course_professors, name="course_professors"),
    url(r'^api/course/(?P<course_id>[0-9].*)/vote', views.vote, name="vote"),

    # authentication
    url(r'^accounts/signup$', views.signup, name="signup"),
    url(r'^accounts/login/$', views.auth_login, name="auth_login"),
    url(r'^accounts/logout$', views.auth_logout, name="auth_logout"),
    url(r'^accounts/confirmation$', views.confirmation, name="confirmation"),

    # password resets
    url(r'^accounts/password/reset/$', authviews.password_reset,
        {
            'post_reset_redirect': '/accounts/password/reset/done/',
            'template_name': 'password_reset_form.html',
            'html_email_template_name': 'password_reset_email.html',
            'email_template_name': 'password_reset_email.html',
        },
        name="password_reset"),
    url(r'^accounts/password/reset/done/$', authviews.password_reset_done,
        {'template_name': 'password_reset_done.html'}),
    url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        authviews.password_reset_confirm,
        {
            'post_reset_redirect': '/accounts/password/done/',
            'template_name': 'password_reset_confirm.html'
        },
        name="password_reset_confirm"),
    url(r'^accounts/password/done/$', authviews.password_reset_complete,
        {'template_name': 'password_reset_complete.html'}),
]
