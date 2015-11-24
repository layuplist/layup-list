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

DEFAULT_FILENAME = "data/undergraduate_courses.json"


MEDIAN_DIR = "./data/medians"

ERROR_LOG = "./median_importer_errors.log"


with open(ERROR_LOG, "w") as logfile:
    for f in os.listdir(MEDIAN_DIR):
        curr_file = os.path.join(MEDIAN_DIR, f)

        if not os.path.isfile(curr_file):
            logfile.write("invalid filename: " + curr_file + "\n")

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

                            # some courses missing subnumbers...so getting a list
                            # instead
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
                                    "Failed to query database for. Will create a new instance of course: " + curr + "\n")

                            # for all the sections of that course
                            for course in course_matches:
                                print course

                                try:
                                    course = Course.objects.get(
                                        department=department,
                                        number=number,
                                        subnumber=section
                                    )

                                # resolve the duplicate key issue - only do it when it doesn't exist
                                except Course.DoesNotExist:
                                    ret = course.coursemedian_set.create(
                                        section=section,
                                        enrollment=enrollment,
                                        median=median,
                                        term=term
                                    )

                    except DataError:
                        print "Data error for: ", curr

                    except IntegrityError:
                        logfile.write(
                            "Unique constraint violated for: " + curr + "\n")


# filename = DEFAULT_FILENAME if len(sys.argv) == 1 else sys.argv[1]

# with transaction.atomic():
#     with open(filename) as data_file:

#         course_list = json.load(data_file)
#         for c in course_list:

#             title = c["course_name"].encode('utf-8')
#             print "importing {}".format(title)
#             department = c["department"]
#             number = int(c["number"])
#             subnumber = int(c["subnumber"]) if "subnumber" in c else None
#             url = c["url"]

#             try:
#                 course = Course.objects.get(
#                     department=department,
#                     number=number,
#                     subnumber=subnumber
#                 )
#                 course.title = title
#                 course.url = url
#                 course.save
#             except Course.DoesNotExist:
#                 Course.objects.create(
#                     title=title,
#                     department=department,
#                     number=number,
#                     subnumber=subnumber,
#                     url=url,
#                 )
