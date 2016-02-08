from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

class Vote(models.Model):

    class Categories:
        GOOD = "GOOD"
        LAYUP = "LAYUP"
        CHOICES = (
            (GOOD, "Good"),
            (LAYUP, "Layup"),
        )

    value = models.IntegerField(default=0)
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=8, choices=Categories.CHOICES, db_index=True)

    class Meta:
        unique_together = ("course", "user", "category")
