"""
Imports reviews from json blob of CoursePicker reviews

to run: python scripts/importers/import_medians.py
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

OLD_REVIEWS = "./data/reviews/old_reviews.json"
NEW_REVIEWS = "./data/reviews/new_reviews.json"


ambiguous_course = 0
missing_course = 0
processed = 0

for f in (OLD_REVIEWS, NEW_REVIEWS):
    with transaction.atomic():
        with open(f) as data_file:
            reviews = json.load(data_file)

            for review in reviews:
                try:
                    department = review["department"]
                    number = review["number"]
                except KeyError:
                    print "Dumping Review, missing critical data"
                    missing_course += 1
                    continue

                # useful, but not essential
                try:
                    professor = review["professor"]
                except KeyError:
                    professor = ""

                try:
                    term = review["term"]
                except KeyError:
                    term = ""

                try:
                    if f == OLD_REVIEWS:
                        comments = review["comments"]["oldReview"]
                    elif f == NEW_REVIEWS:
                        comments = "Course: " + review["comments"]["course"] + "\n\n" + "Professor: " + review[
                            "comments"]["professor"] + "\n\n" + "Workload: " + review["comments"]["workload"] + "\n\n"
                except KeyError:
                    # person writing review left it blank
                    comments = ""

                print department, number, professor, term, comments

                try:
                    # unfortunately reviews don't have subnumbers
                    course = Course.objects.get(
                        department=department,
                        number=number
                    )
                    user = User.objects.get(
                        username="CoursePicker"
                    )
                except Course.DoesNotExist:
                    print "Could not find course for {}{} professor {}".format(
                        department, number, professor
                    )
                    missing_course += 1
                    continue

                except Course.MultipleObjectsReturned:
                    print "Ambiguous course for {}{} professor {}".format(
                        department, number, professor
                    )
                    ambiguous_course += 1
                    continue

                except User.DoesNotExist:
                    user = User.objects.create_user(
                        username="CoursePicker", password=User.objects.make_random_password())

                    print "Could not find user: ", source, " creating now"


                review = Review.objects.create(
                    course=course,
                    user=user,
                    professor=professor,
                    term=term,
                    comments=comments
                )
                processed += 1

print "missing {}, ambiguous {}, processed {}".format(
    missing_course, ambiguous_course, processed
)
