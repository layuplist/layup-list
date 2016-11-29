# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('department', models.CharField(max_length=4, db_index=True)),
                ('number', models.IntegerField(db_index=True)),
                ('subnumber', models.IntegerField(null=True, db_index=True)),
                ('url', models.URLField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='course',
            unique_together=set([('department', 'number', 'subnumber')]),
        ),
    ]
