from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from lib import constants


class StudentManager(models.Manager):
    VALID_YEARS = set([str(year) for year in range(16, 21)])

    def is_valid_dartmouth_student_email(self, email):
        e = email.split("@")

        if len(e) < 2:
            return False

        dnd_name = e[0]
        domain = e[1] # will be 'alumni' for alumni emails
        if domain != "dartmouth.edu":
            return False

        dnd_parts = dnd_name.split('.')

        if dnd_parts[-1] not in self.VALID_YEARS: # dnd student names end in number
            return False

        return True

class Student(models.Model):
    objects = StudentManager()

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    confirmation_link = models.CharField(max_length=16)

    first_name = models.CharField(null=True, max_length=255, db_index=True)
    last_name = models.CharField(null=True, max_length=255, db_index=True)

    score = models.IntegerField(null=True)
    upvotes = models.IntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{} {}: has a score of {} with {} upvotes".format(self.first_name, self.last_name, self.score, self.upvotes)

    def send_confirmation_link(self, request):
        full_link = request.build_absolute_uri(reverse('confirmation')) + '?link=' + self.confirmation_link
        send_mail(
            'Your confirmation link',
            'Please navigate to the following confirmation link: ' +
            full_link, constants.SUPPORT_EMAIL,
            [self.user.username], fail_silently=False
        )
