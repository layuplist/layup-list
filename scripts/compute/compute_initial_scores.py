"""
Compute initial scores for courses using legacy layup lists (layup_score) and
textual analysis of course picker reviews (quality_score)

Should only be run before initial deployment, as this script WILL double count.

to run: python scripts/compute/compute_initial_scores.py
"""
import os
import sys
import django
import json
import re
from collections import Counter
from django.db import transaction

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "layup_list.settings")
django.setup()

from web.models import Course, CourseOffering

TEST_TERM = "16W"
LEGACY_LAYUPS_FILE = "./data/layups/layups.json"
QUALITY_WORDS = ["enjoy", "love", "awesome", "enthusiastic", "passionate", "personal"]

def compute_and_import_initial_scores():
    with transaction.atomic():

        compute_and_import_initial_layup_scores()
        compute_and_import_initial_quality_scores()

        print "---- OVERALL LAYUP ----"
        for c in Course.objects.order_by("-layup_score")[:50]:
            print c, c.layup_score

        print "---- {} LAYUP ----".format(TEST_TERM)
        for c in CourseOffering.objects.select_related("course").filter(term=TEST_TERM).order_by("-course__layup_score")[:50]:
            print c.course, c.course.layup_score

        print "---- OVERALL GOOD ----"
        for c in Course.objects.order_by("-quality_score")[:50]:
            print c, c.quality_score

        print "---- {} GOOD ----".format(TEST_TERM)
        for c in CourseOffering.objects.select_related("course").filter(term=TEST_TERM).order_by("-course__quality_score")[:50]:
            print c.course, c.course.quality_score

def compute_and_import_initial_layup_scores():
    legacy_layup_references, llr_with_comments = initialize_legacy_layup_references()
    for course in Course.objects.all():
        initialize_layup_score(course, legacy_layup_references, llr_with_comments)

def compute_and_import_initial_quality_scores():
    for course in Course.objects.all():
        initialize_quality_score(course)

def initialize_layup_score(course, legacy_layup_references, llr_with_comments):
    course.layup_score = calculate_initial_layup_score(course, legacy_layup_references, llr_with_comments)
    course.save()

def initialize_quality_score(course):
    course.quality_score = calculate_initial_quality_score(course)

    # giving WRIT005 a score of 0 as people don't choose to take this class
    # FWIW, it's #1 otherwise
    if course.department == "WRIT" and course.number == 5:
        course.quality_score = 0

    course.save()

def initialize_legacy_layup_references():
    """
    Creates dictionaries which represent legacy layup lists (circulated spreadsheets)
    The first with number of mentions, the second with number of mentions w/ comments

    Returns nested dictionaries:
    department dict -> number dict -> frequency in layup lists
    """
    legacy_layup_references = {}
    llr_with_comments = {}
    with open(LEGACY_LAYUPS_FILE) as data_file:
        layups = json.load(data_file)

        for layup in layups:
            department = layup["department"]
            number = int(layup["number"])

            if not department in legacy_layup_references:
                legacy_layup_references[department] = Counter()
                llr_with_comments[department] = Counter()

            legacy_layup_references[department][number] += 1
            if "comment" in layup and layup["comment"] != "":
                llr_with_comments[department][number] += 1

    return legacy_layup_references, llr_with_comments


def calculate_initial_layup_score(course, legacy_layup_references, llr_with_comments):
    """
    Raw score is calculated by the number of appearances of the course in
    layup lists circulated in spreadsheets through blitz in the past added with
    the number of those appearances that had an accompanying comment.

    The ultimate score calculated is this raw score multiplied by 2.5, rounded up.
    """
    try:
        legacy_mentions = legacy_layup_references[course.department][course.number]
        legacy_mentions_with_comment = llr_with_comments[course.department][course.number]
    except KeyError:
        return 0

    raw_score = legacy_mentions + legacy_mentions_with_comment
    return int(raw_score * 2.5 + 1)

def calculate_initial_quality_score(course):
    """
    Raw score is calculated using the number of reviews which contain one or more
    of the QUALITY_WORDS.

    QUALITY_WORDS is a collection of words that were chosen based on their
    ability to meaningfully indicate whether a course is good and their relative
    infrequency compared to words like "good" (frequency of words in reviews
    was actually calculated to determine this)

    The final score is weighted by the number of reviews.
    This is achieved through multiplying the raw score by 1 minus 70 percent
    of the proportion of reviews which were not quality indicators, rounded up.
    """
    raw_score = 0
    for review in course.review_set.all():
        text = review.comments.lower()
        for keyword in QUALITY_WORDS:
            if keyword in text:
                raw_score += 1
                break

    review_count = course.review_set.count()
    if review_count == 0:
        return 0

    p_not_triggered = float(review_count - raw_score) / review_count
    return int(raw_score * (1 - p_not_triggered * 0.7) + 1)

if __name__ == '__main__':
    compute_and_import_initial_scores()
