from __future__ import unicode_literals
from django.db import models
from lib import constants


class CourseOfferingManager(models.Manager):

    def course_ids_for_term(self, term=constants.CURRENT_TERM):
        return self.filter(
            term=term
        ).values_list('course_id', flat=True).distinct()


class CourseOffering(models.Model):
    objects = CourseOfferingManager()

    course = models.ForeignKey("Course")
    instructors = models.ManyToManyField("Instructor")

    term = models.CharField(max_length=4, db_index=True)
    section = models.IntegerField()
    period = models.CharField(max_length=64, db_index=True)
    limit = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Legacy
    course_registration_number = models.IntegerField(null=True)

    class Meta:
        unique_together = ("term", "course", "section")

    def __unicode__(self):
        return "{} {}".format(self.term, self.course.short_name())

    def instructors_string(self, separator=", "):
        return separator.join([i.name for i in self.instructors.all()])
