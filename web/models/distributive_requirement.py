from __future__ import unicode_literals
from django.db import models


class DistributiveRequirement(models.Model):
    WORLD_CULTURE = "WC"
    DISTRIBUTIVE = "DIST"
    DISTRIBUTE_TYPE_CHOICES = (
        (WORLD_CULTURE, "World Culture"),
        (DISTRIBUTIVE, "Distributive"),
    )

    name = models.CharField(max_length=16, unique=True)
    distributive_type = models.CharField(
        max_length=16, choices=DISTRIBUTE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name
