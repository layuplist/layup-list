"""
Imports courses from json blob produced by crawl_medians.js

to run: python scripts/importers/import_medians.py
"""
import os
import sys
import django
import json
from django.db import transaction, IntegrityError, DataError

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "layup_list.settings")
django.setup()
from web.models import Course, CourseMedian
from importer_library import clean_department_code

MEDIAN_DIR = "./data/medians"

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

                    department = clean_department_code(
                        m["course"]["department"])

                    number = int(m["course"]["number"])
                    try:
                        subnumber = int(m["course"]["subnumber"])
                    except (KeyError, ValueError):
                        subnumber = None
                    section = int(m["section"])
                    enrollment = int(m["enrollment"])
                    median = m["median"].strip()
                    term = m["term"].strip()

                    try:
                        course = Course.objects.get(
                            department=department,
                            number=number,
                            subnumber=subnumber
                        )
                    except Course.DoesNotExist:
                        print (
                            "Could not find course for {}{}.{} term {}".format(
                                department, number, subnumber, term
                            ))
                        missing_course += 1
                        continue

                    try:
                        m = CourseMedian.objects.get(
                            course=course,
                            section=section,
                            term=term
                        )
                        m.enrollment = enrollment
                        m.median = median
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

print "missing {}, processed {}".format(missing_course, processed)
