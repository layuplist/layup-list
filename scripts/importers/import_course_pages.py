"""
Imports course page info from json blob produced by crawl_course_pages.py

to run: python scripts/importers/import_course_pages.py
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

COURSE_PAGES_FILE = "data/course_pages.json"


def import_course_pages():
    with open(COURSE_PAGES_FILE) as data_file:
        with transaction.atomic():
            for course_page in json.load(data_file):
                import_course_page(course_page)


def import_course_page(course_page):
    # currently only imports descriptions, although we could do more
    course = Course.objects.get(
        department=course_page["department"],
        number=int(re.sub("[^0-9]", "", course_page["number"])),
        subnumber=course_page.get("subnumber")
    )
    course.description = course_page.get("description")
    course.save()

if __name__ == '__main__':
    import_course_pages()
