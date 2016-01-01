"""
Imports courses from json blob produced by crawl_orc_courses.js

to run: python scripts/importers/import_orc_courses.py
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
from web.models import Course

DEFAULT_FILENAME = "data/orc_courses.json"
filename = DEFAULT_FILENAME if len(sys.argv) == 1 else sys.argv[1]

with transaction.atomic():
    with open(filename) as data_file:

        course_list = json.load(data_file)
        for c in course_list:

            title = c["course_name"].encode('utf-8').strip()
            print "importing {}".format(title)
            department = c["department"].strip()
            number = int(re.sub("[^0-9]", "", c["number"]))
            if number > 999:
                print "Bad course number {}:{}".format(department, number)
                raise Exception
            subnumber = int(c["subnumber"]) if "subnumber" in c else None
            url = c["url"].strip()

            try:
                course = Course.objects.get(
                    department=department,
                    number=number,
                    subnumber=subnumber,
                )
                course.title = title
                course.url = url
                course.source = Course.SOURCES.ORC
                course.save
            except Course.DoesNotExist:
                Course.objects.create(
                    title=title,
                    department=department,
                    number=number,
                    subnumber=subnumber,
                    url=url,
                    source=Course.SOURCES.ORC,
                )
