from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Student(models.Model):
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
