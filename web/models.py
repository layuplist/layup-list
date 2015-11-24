from __future__ import unicode_literals
from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=4, db_index=True)
    number = models.IntegerField(db_index=True)
    subnumber = models.IntegerField(null=True, db_index=True)
    url = models.URLField()

    def __unicode__(self):
        if self.subnumber:
            return "{} {}.{}: {}".format(self.department, self.number, self.subnumber, self.title)
        else:
            return "{} {}: {}".format(self.department, self.number, self.title)

    class Meta:
        unique_together = ("department", "number", "subnumber")


class CourseMedian(models.Model):
    course = models.ForeignKey(Course)
    section = models.IntegerField()
    enrollment = models.IntegerField()
    median = models.CharField(max_length=6, db_index=True)
    term = models.CharField(max_length=4, db_index=True)

    class Meta:
        unique_together = ("course", "section", "term")
