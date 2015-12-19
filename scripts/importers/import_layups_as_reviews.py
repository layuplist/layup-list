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

from django.contrib.auth.models import User
from web.models import Review, Course

LAYUPS = "./data/layups/layups.json"

ambiguous_course = 0
missing_course = 0
processed = 0
users_created = 0

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

                if len(layup["source"]) <= 4:
                    term = layup["source"]
                else:
                    term = ""

            except KeyError: # just a safeguard against typos from manual spreadsheet cleaning
                print "Dumping Layup Review (improper spreadsheet data)"
                missing_course += 1
                continue

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
                print "Could not find user: ", source, " creating now"

                # security? change this pass to point to env later
                user = User.objects.create_user(username=username, password=User.objects.make_random_password())
                users_created += 1

            except User.MultipleObjectsReturned:
                print "This should never happen: unique username violation"

            review = Review.objects.create(
                course=course,
                user=user,
                professor=professor,
                term=term,
                comments=comments
            )
            processed += 1

print "missing {}, ambiguous {}, processed {}, users_created {}".format(
    missing_course, ambiguous_course, processed, users_created
)

