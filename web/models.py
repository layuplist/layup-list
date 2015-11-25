from __future__ import unicode_literals
from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=4, db_index=True)
    number = models.IntegerField(db_index=True)
    subnumber = models.IntegerField(null=True, db_index=True)
    url = models.URLField()

    def __unicode__(self):
        return "{}: {}".format(self.short_name(), self.title)

    def short_name(self):
        if self.subnumber:
            return "{}{}.{}".format(self.department, self.number, self.subnumber)
        else:
            return "{}{}".format(self.department, self.number)

    class Meta:
        unique_together = ("department", "number", "subnumber")


class CourseMedian(models.Model):
    course = models.ForeignKey(Course)
    section = models.IntegerField()
    enrollment = models.IntegerField()
    median = models.CharField(max_length=6, db_index=True)
    term = models.CharField(max_length=4, db_index=True)

    def __unicode__(self):
        return "{} {}: {}".format(self.term, self.course.short_name(), self.median)

    class Meta:
        unique_together = ("course", "section", "term")
