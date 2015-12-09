from __future__ import unicode_literals
from django.db import models
from course_offering import CourseOffering

class CourseManager(models.Manager):

    def for_term(self, term):
        return self.filter(id__in=CourseOffering.objects.course_ids_for_term(term))

class Course(models.Model):
    objects = CourseManager()

    crosslisted_courses = models.ManyToManyField("self")
    distribs = models.ManyToManyField("DistributiveRequirement")

    class SOURCES():
        ORC = "ORC"
        TIMETABLE = "TIMETABLE"
        CHOICES = (
            (ORC, "Organization, Regulations, and Courses"),
            (TIMETABLE, "Academic Timetable"),
        )

    title = models.CharField(max_length=200)
    department = models.CharField(max_length=4, db_index=True)
    number = models.IntegerField(db_index=True)
    subnumber = models.IntegerField(null=True, db_index=True)
    url = models.URLField(null=True)
    source = models.CharField(max_length=16, choices=SOURCES.CHOICES)

    layup_score = models.IntegerField(default=0)
    quality_score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("department", "number", "subnumber")

    def __unicode__(self):
        return "{}: {}".format(self.short_name(), self.title)

    def short_name(self):
        if self.subnumber:
            return "{0}{1:03d}.{2:02d}".format(self.department, self.number, self.subnumber)
        else:
            return "{0}{1:03d}".format(self.department, self.number)

    def distribs_string(self, separator=", "):
        return separator.join([d.name for d in self.distribs.all()])
