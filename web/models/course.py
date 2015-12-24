from __future__ import unicode_literals
from django.db import models

class Course(models.Model):
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
            return "{}{}.{}".format(self.department, self.number, self.subnumber)
        else:
            return "{}{}".format(self.department, self.number)
