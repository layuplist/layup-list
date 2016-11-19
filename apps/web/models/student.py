from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.conf import settings
from apps.web.models import Review, Vote
from lib import constants


class StudentManager(models.Manager):

    def is_valid_dartmouth_student_email(self, email):
        email_components = email.split("@")
        if len(email_components) != 2:
            return False
        username, domain = email_components
        year = username.split(".")[-1]
        return (
            domain == "dartmouth.edu" and
            len(year) == 2 and
            (year.isdigit() or year.lower() == "ug")
        )


class Student(models.Model):
    objects = StudentManager()

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    confirmation_link = models.CharField(max_length=16, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def send_confirmation_link(self, request):
        full_link = request.build_absolute_uri(
            reverse('confirmation')) + '?link=' + self.confirmation_link
        if not settings.DEBUG:
            send_mail(
                'Your confirmation link',
                'Please navigate to the following confirmation link: ' +
                full_link, constants.SUPPORT_EMAIL,
                [self.user.email], fail_silently=False
            )

    def can_see_recommendations(self):
        return (Vote.objects.num_quality_upvotes_for_user(self.user) >=
                constants.REC_UPVOTE_REQ)

    def __unicode__(self):
        return str(self.user)
