import difflib
import json

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.mail import send_mail
from django.db import models, transaction

from apps.spider.crawlers import medians
from apps.spider import utils

from lib import constants


class CrawledDataManager(models.Manager):

    def handle_new_crawled_data(self, new_data, resource_name, data_type):
        db_data, created = self.update_or_create(
            resource=resource_name,
            data_type=data_type,
            defaults={"pending_data": new_data},
        )
        if created or db_data.has_change():
            db_data.email_change()
            if settings.AUTO_IMPORT_CRAWLED_DATA:
                db_data.approve_change()
            return True
        return False

    def pending_first(self):
        return (
            [d for d in self.all() if d.has_change()] +
            [d for d in self.all() if not d.has_change()]
        )


class CrawledData(models.Model):
    MEDIANS = "medians"
    ORC_DEPARTMENT_COURSES = "orc_department_courses"
    COURSE_TIMETABLE = "course_timetable"
    DATA_TYPE_CHOICES = (
        (MEDIANS, "Medians"),
        (ORC_DEPARTMENT_COURSES, "ORC Department Courses"),
        (COURSE_TIMETABLE, "Course Timetable"),
    )
    objects = CrawledDataManager()

    resource = models.CharField(max_length=128, db_index=True, unique=True)
    data_type = models.CharField(max_length=32, choices=DATA_TYPE_CHOICES)
    pending_data = JSONField()
    current_data = JSONField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "[{data_type}] {resource}".format(
            data_type=self.data_type,
            resource=self.resource,
        )

    def has_change(self):
        return self.pending_data != self.current_data

    @property
    def diff(self):
        if not self.current_data:
            return utils.pretty_json(self.pending_data)
        if self.has_change:
            return "\n".join(difflib.unified_diff(
                utils.pretty_json(self.current_data).splitlines(),
                utils.pretty_json(self.pending_data).splitlines(),
            ))

    @property
    def pretty_current_data(self):
        return utils.pretty_json(self.current_data)

    def email_change(self):
        assert self.has_change()
        send_mail(
            "[{type}][{resource}][{pk}] New Import".format(
                type=self.data_type,
                resource=self.resource,
                pk=self.pk,
            ),
            self.diff,
            constants.SUPPORT_EMAIL,
            [email for _, email in settings.ADMINS],
            fail_silently=False,
        )

    def approve_change(self):
        from apps.spider.tasks import import_pending_crawled_data
        import_pending_crawled_data.delay(self.pk)
