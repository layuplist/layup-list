# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20151124_0738'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseOffering',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('term', models.CharField(max_length=4, db_index=True)),
                ('course_registration_number', models.IntegerField(unique=True)),
                ('period', models.CharField(max_length=64, db_index=True)),
                ('section', models.IntegerField()),
                ('limit', models.IntegerField(null=True)),
                ('course', models.ForeignKey(to='web.Course')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DistributiveRequirement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=16)),
                ('distributive_type', models.CharField(max_length=16, choices=[('WC', 'World Culture'), ('DIST', 'Distributive')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='courseoffering',
            name='instructors',
            field=models.ManyToManyField(to='web.Instructor'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='courseoffering',
            unique_together=set([('term', 'course', 'section')]),
        ),
        migrations.AddField(
            model_name='course',
            name='crosslisted_courses',
            field=models.ManyToManyField(related_name='crosslisted_courses_rel_+', to='web.Course'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='distribs',
            field=models.ManyToManyField(to='web.DistributiveRequirement'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='source',
            field=models.CharField(default='ORC', max_length=16, choices=[('ORC', 'Organization, Regulations, and Courses'), ('TIMETABLE', 'Academic Timetable')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='course',
            name='url',
            field=models.URLField(null=True),
            preserve_default=True,
        ),
    ]
