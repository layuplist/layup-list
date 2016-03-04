from __future__ import unicode_literals
from django.db import models


class CourseMedian(models.Model):
    course = models.ForeignKey("Course")

    section = models.IntegerField()
    enrollment = models.IntegerField()
    median = models.CharField(max_length=6, db_index=True)
    term = models.CharField(max_length=4, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{} {}: {}".format(self.term, self.course.short_name(), self.median)

    class Meta:
        unique_together = ("course", "section", "term")
