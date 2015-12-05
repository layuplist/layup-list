# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_auto_20151203_1925'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 5, 14, 32, 31, 301928, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='course',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 5, 14, 32, 33, 38087, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='coursemedian',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 5, 14, 32, 35, 517939, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='coursemedian',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 5, 14, 32, 39, 141988, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='courseoffering',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 5, 14, 32, 42, 93924, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='courseoffering',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 5, 14, 32, 45, 165774, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='distributiverequirement',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 5, 14, 32, 55, 60777, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='distributiverequirement',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 5, 14, 32, 56, 484768, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='instructor',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 5, 14, 32, 57, 836717, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='instructor',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 5, 14, 32, 59, 564617, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
