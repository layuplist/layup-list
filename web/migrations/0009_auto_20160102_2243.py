# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-02 22:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0008_student'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='user',
        ),
        migrations.DeleteModel(
            name='Student',
        ),
    ]