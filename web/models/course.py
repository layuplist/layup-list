from __future__ import unicode_literals
from django.db import models
from course_offering import CourseOffering
from django.core.urlresolvers import reverse
import re


class CourseManager(models.Manager):
    course_search_regex = re.compile("^(?P<department_or_query>\D*)(?P<number>\d*)\.?(?P<subnumber>\d*)(?P<other>.*)")
    DEPARTMENT_LENGTHS = [3,4]

    def for_term(self, term):
        return self.filter(id__in=CourseOffering.objects.course_ids_for_term(term))

    def search(self, query):
        query_data = {
            k: v.strip()
            for k, v in self.course_search_regex.match(query).groupdict().iteritems()
        }

        department_or_query = query_data["department_or_query"]
        number = query_data["number"]
        subnumber = query_data["subnumber"]
        other = query_data["other"]

        if not department_or_query:
            return self.none()
        elif len(department_or_query) not in self.DEPARTMENT_LENGTHS:
            # must be query, too long to be department. ignore numbers we may have.
            # e.g. "Introduction"
            return Course.objects.filter(title__icontains=department_or_query)
        elif number and subnumber:
            # course with number and subnumber
            # e.g. COSC 089.01
            return Course.objects.filter(
                department__iexact=department_or_query,
                number=number,
                subnumber=subnumber
            )
        elif number:
            # course with number, could be ambiguous
            # e.g. COSC 001
            return Course.objects.filter(
                department__iexact=department_or_query,
                number=number
            )
        else:
            # could be either department or query
            # e.g. "COSC" (department) or "War" (query)
            courses = Course.objects.filter(
                department__iexact=department_or_query,
            ).order_by("number", "subnumber")
            if len(courses) == 0:
                return Course.objects.filter(title__icontains=department_or_query)
            return courses


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
    description = models.TextField(null=True)

    layup_score = models.IntegerField(default=0)
    quality_score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("department", "number", "subnumber")

    def __unicode__(self):
        return "{}: {}".format(self.short_name(), self.title)

    def get_absolute_url(self):
        return reverse('course_detail', args=[self.id])

    def short_name(self):
        if self.subnumber:
            return "{0}{1:03d}.{2:02d}".format(self.department, self.number, self.subnumber)
        else:
            return "{0}{1:03d}".format(self.department, self.number)

    def distribs_string(self, separator=", "):
        return separator.join([d.name for d in self.distribs.all()])
