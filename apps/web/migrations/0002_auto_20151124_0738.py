# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseMedian',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('section', models.IntegerField()),
                ('enrollment', models.IntegerField()),
                ('median', models.CharField(max_length=6, db_index=True)),
                ('term', models.CharField(max_length=4, db_index=True)),
                ('course', models.ForeignKey(to='web.Course')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='coursemedian',
            unique_together=set([('course', 'section', 'term')]),
        ),
    ]
