from __future__ import unicode_literals
from django.db import models

class CourseOffering(models.Model):
    course = models.ForeignKey("Course")
    instructors = models.ManyToManyField("Instructor")

    term = models.CharField(max_length=4, db_index=True)
    course_registration_number = models.IntegerField(unique=True)
    section = models.IntegerField()
    period = models.CharField(max_length=64, db_index=True)
    limit = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("term", "course", "section")

    def __unicode__(self):
        return "{} {}".format(self.term, self.course.short_name())
