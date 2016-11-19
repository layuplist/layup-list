# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-19 08:13
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CrawledData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource', models.CharField(db_index=True, max_length=128, unique=True)),
                ('data_type', models.CharField(choices=[(b'medians', b'Medians')], max_length=32)),
                ('pending_data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('current_data', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
