"""
Imports courses from json blob produced by crawl_undergraduate_courses.js

to run: python scripts/importers/import_undergraduate_courses.py
"""
import os
import sys
import django
import json
from django.db import transaction, IntegrityError, DataError
import subprocess

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "layup_list.settings")
django.setup()
from web.models import Course, CourseMedian

MEDIAN_DIR = "./data/medians"
DEPARTMENT_CORRECTIONS = {
    "M&amp;SS": "M&SS"
}

ambiguous_subnumber = 0
missing_course = 0
processed = 0

for f in os.listdir(MEDIAN_DIR):
    curr_file = os.path.join(MEDIAN_DIR, f)

    if not os.path.isfile(curr_file):
        logfile.write("The following is not a file: " + curr_file + "\n")

    elif not curr_file.lower().endswith(".json"):
        logfile.write("Not a JSON file: " + curr_file + "\n")

    else:
        with transaction.atomic():
            with open(curr_file) as data_file:
                medians = json.load(data_file)
                for m in medians:

                    department = m["course"]["department"].strip()
                    if department in DEPARTMENT_CORRECTIONS:
                        department = DEPARTMENT_CORRECTIONS[department]

                    number = int(m["course"]["number"])
                    try:
                        subnumber = int(m["course"]["subnumber"])
                    except (KeyError, ValueError):
                        subnumber = None
                    section = int(m["section"])
                    enrollment = int(m["enrollment"])
                    median = m["median"].strip()
                    term = m["term"].strip()

                    course = None
                    try:
                        course = Course.objects.get(
                            department=department,
                            number=number,
                            subnumber=subnumber
                        )
                    except Course.DoesNotExist:
                        try:
                            # subnumber may have been missing or incorrect
                            course = Course.objects.get(
                                department=department,
                                number=number,
                            )
                        except Course.DoesNotExist:
                            print "Could not find course for {}{}.{} term {}".format(
                                department, number, subnumber, term
                            )
                            missing_course += 1
                        except Course.MultipleObjectsReturned:
                            print "Ambiguous course for {}{}.{} term {}".format(
                                department, number, subnumber, term
                            )
                            ambiguous_subnumber += 1

                    if course is not None:
                        try:
                            m = CourseMedian.objects.get(
                                course=course,
                                section=section,
                                term=term
                            )
                            m.enrollment = enrollment
                            m.term = term
                            m.save
                        except CourseMedian.DoesNotExist:
                            course.coursemedian_set.create(
                                section=section,
                                enrollment=enrollment,
                                median=median,
                                term=term
                            )
                        processed += 1

print "missing {}, ambiguous {}, processed {}".format(
    missing_course, ambiguous_subnumber, processed
)
