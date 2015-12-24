from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    course = models.ForeignKey("Course")
    user = models.ForeignKey(User)

    professor = models.CharField(max_length=255, db_index=True)
    term = models.CharField(max_length=4, db_index=True)
    comments = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{} {} {}: {}".format(self.course.short_name(), self.professor, self.term, self.comments)
