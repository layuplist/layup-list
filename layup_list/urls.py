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
from django.conf.urls import url
from django.contrib import admin
from web import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.landing, name="landing"),
    url(r'^signup$', views.signup, name="signup"),
    url(r'^accounts/login/$', views.auth_login, name="auth_login"),
    url(r'^accounts/logout$', views.auth_logout, name="auth_logout"),
    url(r'^confirmation$', views.confirmation, name="confirmation"),
    url(r'^current_term$', views.current_term, name="current_term"),
    url(r'^course/(?P<course_id>[0-9].*)$', views.course_detail, name="course_detail"),
    url(r'^search/?', views.search, name="search"),
    url(r'^api/medians/(?P<course_id>[0-9].*)', views.medians, name="medians")
]
