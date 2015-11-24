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


with open("./median_importer_errors.log", "w") as logfile:
    for f in os.listdir(MEDIAN_DIR):
        curr_file = os.path.join(MEDIAN_DIR, f)

        if not os.path.isfile(curr_file):
            logfile.write("The following is not a file: " + curr_file + "\n")

        elif not curr_file.lower.endswith(".json"):
            logfile.write("Not a JSON file: " + curr_file + "\n")

        else:
            with open(curr_file) as data_file:
                medians = json.load(data_file)

                for m in medians:
                    curr = (m["course"]["department"] +
                            m["course"]["number"]).encode('utf-8')
                    print "importing {}".format(curr)

                    department = m["course"]["department"]

                    # malformated crawled string for M&SS
                    if department == "M&amp;SS":
                        department = "M&SS"

                    number = int(m["course"]["number"])

                    section = int(m["section"])
                    enrollment = int(m["enrollment"])
                    median = m["median"]
                    term = m["term"]

                    try:
                        with transaction.atomic():

                            # some courses are missing subnumbers...so getting
                            # querying for a list instead
                            course_matches = Course.objects.filter(
                                department=department,
                                number=number
                            )

                            # ORC missing the course in catalog...but a median
                            # exists for it
                            if len(course_matches) == 0:
                                Course.objects.create(
                                    title="",
                                    department=department,
                                    number=number,
                                    subnumber=section,
                                    url=""
                                )
                                logfile.write(
                                    "Failed to query course table for current median. Will create a new instance of course: " + curr + "\n")

                            # for all the sections of that course
                            for course in course_matches:
                                print course

                                try:
                                    course = Course.objects.get(
                                        department=department,
                                        number=number,
                                        subnumber=section
                                    )

                                # resolve the duplicate key issue - only do this
                                # when it doesn't exist
                                except Course.DoesNotExist:
                                    ret = course.coursemedian_set.create(
                                        section=section,
                                        enrollment=enrollment,
                                        median=median,
                                        term=term
                                    )

                    except DataError:
                        logfile.write("Data error for: " + curr + "\n")

                    except IntegrityError:
                        logfile.write(
                            "Unique constraint violated for: " + curr + "\n")
