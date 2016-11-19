from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from apps.web.models import Course, CourseOffering, Vote


class GroupedRecommendation(object):

    def __init__(self, course):
        self.course = course
        self.weight = 0.0
        self.recs = []

    def reason(self):
        return " ".join([r.course.short_name() for r in self.recs])


class RecommendationManager(models.Manager):

    def for_user(self, user, all_terms=False):

        interacted_courses = Vote.objects.filter(user=user).exclude(value=0)
        interacted_course_ids = interacted_courses.values_list(
            'course_id', flat=True)
        crosslisted_interacted_course_ids = Course.objects.filter(
            crosslisted_courses__in=interacted_course_ids).values_list(
            'id', flat=True)
        upvoted_course_ids = interacted_courses.filter(
            value=1, category=Vote.CATEGORIES.QUALITY).values_list(
            'course_id', flat=True)

        recommendations = (
            self
            .filter(course_id__in=upvoted_course_ids)
            .exclude(
                Q(recommendation_id__in=interacted_course_ids) |
                Q(recommendation_id__in=crosslisted_interacted_course_ids))
            )

        if not all_terms:
            recommendations = recommendations.filter(
                recommendation_id__in=CourseOffering.objects.
                course_ids_for_term())

        recommendations = recommendations.prefetch_related(
            'course', 'recommendation',
            'recommendation__distribs',
            'recommendation__review_set',
            'recommendation__courseoffering_set').order_by("-weight")[:500]

        grouped_recs = {}
        for rec in recommendations:
            grouped_recs[rec.recommendation] = grouped_recs.get(
                rec.recommendation,
                GroupedRecommendation(rec.recommendation))
            grouped_recs[rec.recommendation].weight += rec.weight
            grouped_recs[rec.recommendation].recs.append(rec)

        sorted_grouped_recs = sorted(
            grouped_recs.values(), key=lambda x: -x.weight)

        return sorted_grouped_recs[:30]


class Recommendation(models.Model):
    objects = RecommendationManager()

    DOCUMENT_SIMILARITY = "docsim"
    CREATORS = (
        (DOCUMENT_SIMILARITY, "Document Similarity"),
    )

    course = models.ForeignKey("web.Course", related_name="recommendations")
    recommendation = models.ForeignKey(
        "web.Course", related_name="recommenders")

    creator = models.CharField(max_length=16, choices=CREATORS)
    weight = models.FloatField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{} {} -> {}".format(
            self.weight, self.course.short_name(), self.recommendation)
