"""
Imports reviews from json blob of layups

to run: python scripts/importers/import_layups_as_reviews.py
"""

import os
import sys
import django
import json
import re
from django.db import transaction

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "layup_list.settings")
django.setup()

from django.contrib.auth.models import User, Group
from web.models import Review, Course
from importer_library import clean_department_code

import HTMLParser

html_parser = HTMLParser.HTMLParser()

LAYUPS = "./data/layups/layups.json"

ambiguous_course = 0
missing_course = 0
processed = 0
users_created = 0
empty_review = 0

with transaction.atomic():
    with open(LAYUPS) as data_file:
        layups = json.load(data_file)

        for layup in layups:
            try:
                department = clean_department_code(layup["department"])
                number = layup["number"]
                course_name = layup["course_name"]
                professor = layup["instructor"]
                comments = layup["comments"]

                if len(layup["source"]) == 3 and re.match(r'[0-9][0-9][W,F,S,X]', layup["source"]):
                    term = layup["source"]
                else:
                    term = ""

            except KeyError: # just a safeguard against typos from manual spreadsheet cleaning
                print "Dumping Layup Review (improper spreadsheet data)"
                missing_course += 1
                continue

            if comments == "":
                empty_review += 1
                continue
            comments = html_parser.unescape(comments)

            print department, number, course_name, professor, comments

            try:
                course = Course.objects.get(
                    department=department,
                    number=number
                )
                user = User.objects.get(
                    username=layup["source"]
                )

            except Course.DoesNotExist:
                print "Could not find course for {}{} course_name {} professor {}".format(
                    department, number, course_name, professor
                )
                missing_course += 1
                continue

            except Course.MultipleObjectsReturned:
                print "Ambiguous course for {}{} course_name {} professor {}".format(
                    department, number, course_name, professor
                )
                ambiguous_course += 1
                continue

            except User.DoesNotExist:
                print "Could not find user: ", layup["source"], " creating now"
                user = User.objects.create_user(username=layup["source"], password=User.objects.make_random_password())
                user.groups.add(Group.objects.get_or_create(name="DummyUsers")[0])
                user.groups.add(Group.objects.get_or_create(name="OldLayupListDummyUser")[0])
                users_created += 1

            review = Review.objects.create(
                course=course,
                user=user,
                professor=professor,
                term=term,
                comments=comments
            )
            processed += 1

print "missing {}, ambiguous {}, processed {}, users_created {}, empty review {}".format(
    missing_course, ambiguous_course, processed, users_created, empty_review
)
