"""
Imports courses from json blob produced by crawl_term.js

to run: python scripts/importers/import_term.py [TERM NAME] [FILE]
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
from web.models import (
    Course,
    CourseOffering,
    DistributiveRequirement,
    Instructor,
)

UNDERGRAD_NUMBER_LIMIT = 100


def validate_and_open_file():
    if (len(sys.argv) < 3 or len(sys.argv[1]) != 3 or not
            re.match(r'[0-9][0-9][W,F,S,X]', sys.argv[1])):
        print "usage: import_term.py [TERM NAME] [FILENAME]"
        print ("Term Name must be three characters: two digits and one letter"
               " (F,W,S,X)")
        quit()

    term, filename = sys.argv[1:]

    with transaction.atomic():
        with open(filename) as data_file:
            course_list = json.load(data_file)
            for c in course_list:
                clean_course_data(c)
                if c["number"] < UNDERGRAD_NUMBER_LIMIT:
                    import_cleaned_data(c, term)


def clean_course_data(course_dict):
    course_dict["crn"] = int(course_dict["crn"])

    course_dict["crosslisted"] = None if course_dict[
        "crosslisted"] == '' else course_dict["crosslisted"].split(", ")
    if course_dict["crosslisted"]:
        for i in xrange(0, len(course_dict["crosslisted"])):
            xlist_name = course_dict["crosslisted"][i]
            xlist_split = xlist_name.split()
            xlist_dict = {}
            xlist_dict["program"] = xlist_split[0]
            numbers = xlist_split[1].split(".")
            xlist_dict["number"] = numbers[0]
            xlist_dict["subnumber"] = None if len(numbers) != 2 else numbers[1]
            course_dict["crosslisted"][i] = xlist_dict

    course_dict["distribs"] = None if course_dict[
        "distribs"] == '' else course_dict["distribs"].split(" or ")
    course_dict["instructor"] = None if course_dict[
        "instructor"] == '' else course_dict["instructor"].split(", ")
    course_dict["limit"] = None if course_dict[
        "limit"] == '' else int(course_dict["limit"])
    course_dict["number"] = int(course_dict["number"])
    # course_dict["period"] = course_dict["period"]
    course_dict["program"] = course_dict["program"]
    course_dict["section"] = int(course_dict["section"])
    course_dict["subnumber"] = None if course_dict[
        "subnumber"] == '' else int(course_dict["subnumber"])
    course_dict["title"] = course_dict["title"].encode(
        'ascii', 'ignore').decode('ascii')
    course_dict["world_culture"] = None if course_dict[
        "world_culture"] == '' else course_dict["world_culture"]


def import_cleaned_data(course_dict, term):
    try:
        course = Course.objects.get(
            department=course_dict["program"],
            number=course_dict["number"],
            subnumber=course_dict["subnumber"],
        )
    except Course.DoesNotExist:
        print "Cannot find {}{}.{} {}. Creating...".format(
            course_dict["program"],
            course_dict["number"],
            course_dict["subnumber"],
            course_dict["title"]
        )

        course = Course.objects.create(
            title=course_dict["title"],
            department=course_dict["program"],
            number=course_dict["number"],
            subnumber=course_dict["subnumber"],
            source=Course.SOURCES.TIMETABLE,
        )

    try:
        offering = CourseOffering.objects.get(
            course=course,
            section=course_dict["section"],
            term=term
        )
        offering.period = course_dict["period"]
        offering.limit = course_dict["limit"]
        offering.save()

    except CourseOffering.DoesNotExist:
        offering = CourseOffering.objects.create(
            course=course,
            term=term,
            course_registration_number=course_dict["crn"],
            period=course_dict["period"],
            section=course_dict["section"],
            limit=course_dict["limit"],
        )

    if course_dict["crosslisted"]:
        for c in course_dict["crosslisted"]:
            try:
                xlist_course = Course.objects.get(
                    department=c["program"],
                    number=c["number"],
                    subnumber=c["subnumber"],
                )
                course.crosslisted_courses.add(xlist_course)
            except Course.DoesNotExist:
                # do nothing... course should come up later, we will create it
                # then
                continue

    if course_dict["distribs"]:
        for name in course_dict["distribs"]:
            try:
                distrib = DistributiveRequirement.objects.get(name=name)
            except DistributiveRequirement.DoesNotExist:
                distrib = DistributiveRequirement.objects.create(
                    name=name,
                    distributive_type=DistributiveRequirement.DISTRIBUTIVE
                )
            course.distribs.add(distrib)

    if course_dict["world_culture"]:
        try:
            distrib = DistributiveRequirement.objects.get(
                name=course_dict["world_culture"])
        except DistributiveRequirement.DoesNotExist:
            distrib = DistributiveRequirement.objects.create(
                name=course_dict["world_culture"],
                distributive_type=DistributiveRequirement.WORLD_CULTURE
            )
        course.distribs.add(distrib)

    if course_dict["instructor"]:
        for name in course_dict["instructor"]:
            try:
                instructor = Instructor.objects.get(name=name)
            except Instructor.DoesNotExist:
                instructor = Instructor.objects.create(name=name)
            offering.instructors.add(instructor)

validate_and_open_file()
