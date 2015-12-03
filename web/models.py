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

    class Meta:
        unique_together = ("department", "number", "subnumber")

    def __unicode__(self):
        return "{}: {}".format(self.short_name(), self.title)

    def short_name(self):
        if self.subnumber:
            return "{}{}.{}".format(self.department, self.number, self.subnumber)
        else:
            return "{}{}".format(self.department, self.number)



class CourseOffering(models.Model):
    course = models.ForeignKey("Course")
    instructors = models.ManyToManyField("Instructor")

    term = models.CharField(max_length=4, db_index=True)
    course_registration_number = models.IntegerField(unique=True)
    section = models.IntegerField()
    period = models.CharField(max_length=64, db_index=True)
    limit = models.IntegerField(null=True)

    class Meta:
        unique_together = ("term", "course", "section")

    def __unicode__(self):
        return "{} {}".format(self.term, self.course.short_name())


class DistributiveRequirement(models.Model):
    WORLD_CULTURE = "WC"
    DISTRIBUTIVE = "DIST"
    DISTRIBUTE_TYPE_CHOICES = (
        (WORLD_CULTURE, "World Culture"),
        (DISTRIBUTIVE, "Distributive"),
    )

    name = models.CharField(max_length=16, unique=True)
    distributive_type = models.CharField(max_length=16, choices=DISTRIBUTE_TYPE_CHOICES)

    def __unicode__(self):
        return self.name


class Instructor(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)

    def __unicode__(self):
        return self.name


class CourseMedian(models.Model):
    course = models.ForeignKey("Course")

    section = models.IntegerField()
    enrollment = models.IntegerField()
    median = models.CharField(max_length=6, db_index=True)
    term = models.CharField(max_length=4, db_index=True)

    def __unicode__(self):
        return "{} {}: {}".format(self.term, self.course.short_name(), self.median)

    class Meta:
        unique_together = ("course", "section", "term")
