from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class ReviewManager(models.Manager):

    def user_can_write_review(self, user, course):
        return not self.filter(user=user, course=course).exists()

    def num_reviews_for_user(self, user):
        return self.filter(user=user).count()


class Review(models.Model):
    objects = ReviewManager()

    MANUAL_SENTIMENT_LABELER = "Manual"
    AUTOMATED_SENTIMENT_LABELER = "Classifier"
    SENTIMENT_LABELERS = (
        (MANUAL_SENTIMENT_LABELER, "Sentiment manually recorded"),
        (AUTOMATED_SENTIMENT_LABELER, "Sentiment based on classifier"),
    )

    course = models.ForeignKey("Course")
    user = models.ForeignKey(User)

    professor = models.CharField(max_length=255, db_index=True, blank=False)
    term = models.CharField(max_length=3, db_index=True, blank=False)
    comments = models.TextField(blank=False)

    sentiment_labeler = models.CharField(
        max_length=64, choices=SENTIMENT_LABELERS, default=None,
        db_index=True, null=True, blank=True)
    difficulty_sentiment = models.FloatField(
        default=None, null=True, blank=True)
    quality_sentiment = models.FloatField(default=None, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{} {} {}: {}".format(
            self.course.short_name(), self.professor, self.term, self.comments)
