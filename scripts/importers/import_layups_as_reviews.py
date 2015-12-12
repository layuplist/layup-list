"""
Imports reviews from json blob of layups

to run: python scripts/importers/import_layups_as_reviews.py
"""

import os
import sys
import django
import json
from django.db import transaction

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "layup_list.settings")
django.setup()
from web.models import Review, Course

LAYUPS = "./data/layups/layups.json"

ambiguous_course = 0
missing_course = 0
processed = 0

with transaction.atomic():
    with open(LAYUPS) as data_file:
        layups = json.load(data_file)

        for layup in layups:
            try:
                department = layup["department"]
                number = layup["number"]
                course_name = layup["course_name"]
                professor = layup["instructor"]
                comments = layup["comments"]

            except KeyError:
                print "Dumping Layup Review, missing critical data"
                missing_course += 1
                continue

            print department, number, course_name, professor, comments

            try:
                course = Course.objects.get(
                    department=department,
                    number=number
                )
            except Course.DoesNotExist:
                print "Could not find course for {}{} course_name {} professor {}".format(
                    department, number, course_name, professor
                )
                missing_course += 1
            except Course.MultipleObjectsReturned:
                print "Ambiguous course for {}{} course_name {} professor {}".format(
                    department, number, course_name, professor
                )
                ambiguous_course += 1
            processed += 1

print "missing {}, ambiguous {}, processed {}".format(
    missing_course, ambiguous_course, processed
)

