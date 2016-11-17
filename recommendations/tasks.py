from celery import shared_task
from itertools import chain
import numpy as np
import os
import re
import sys
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from time import time

from django.db import transaction
from django.db.models import Q

from web.models import Course
from recommendations.models import Recommendation

from lib import task_utils


MIN_COURSE_DESCRIPTION_LENGTH = 80
RECOMMENDATIONS_PER_CLASS = 8

PERFORM_TFIDF = True
INCLUDE_REVIEWS = False  # very noisy, turn off


@shared_task
@task_utils.email_if_fails
def generate_course_description_similarity_recommendations():
    t0 = time()
    print "loading word jumbles into memory..."
    course_ids = []
    reverse_course_ids = {}
    course_descriptions = []
    i = 0
    for course in Course.objects.exclude(
            description=None).exclude(description=""):
        if len(course.description) < MIN_COURSE_DESCRIPTION_LENGTH:
            # these are typically uninteresting classes e.g. thesis
            continue
        course_ids.append(course.id)
        reverse_course_ids[course.id] = i
        word_jumble = [_clean_text_to_raw_words(course.description)]
        word_jumble.append(_clean_text_to_raw_words(course.title))
        # reviews are very noisy -- they tend to be similar between classes
        if INCLUDE_REVIEWS:
            for review in course.review_set.all():
                word_jumble.append(_clean_text_to_raw_words(review.comments))
        course_descriptions.append(" ".join(word_jumble))
        i += 1
    print "finished in {}".format(time() - t0)

    t0 = time()
    print "fitting to count vectorizer..."
    count_vect = CountVectorizer()
    corpus = count_vect.fit_transform(course_descriptions)
    print "shape is {}".format(corpus.shape)
    print "finished in {}".format(time() - t0)

    # words -> indices
    # print count_vect.vocabulary_

    if PERFORM_TFIDF:
        t0 = time()
        print "tfidf transform..."
        tfidf_transformer = TfidfTransformer()
        corpus = tfidf_transformer.fit_transform(corpus)
        print "shape is {}".format(corpus.shape)
        print "finished in {}".format(time() - t0)

    # TODO: try applying PCA, see if it improves performance

    t0 = time()
    print "compute cosine similarity "
    pairwise_similarity = corpus * corpus.T
    print "shape is {}".format(pairwise_similarity.shape)
    print "finished in {}".format(time() - t0)

    t0 = time()
    print "calculating and creating recommendations..."
    psarray = pairwise_similarity.toarray()

    # zero out columns corresponding to thesis, research, independent, and grad
    course_ids_to_zero = Course.objects.filter(
        Q(title__icontains="thesis") |
        Q(title__icontains="research") |
        Q(title__icontains="independent") |
        Q(title__icontains="seminar") |
        Q(title__icontains="first-year") |
        Q(title__icontains="foreign study") |
        Q(title__icontains="senior") |
        Q(title__icontains="honors") |
        Q(number__gt=99)
    ).values_list("id", flat=True)
    for zero_id in course_ids_to_zero:
        if zero_id in reverse_course_ids:
            psarray[:, reverse_course_ids[zero_id]] = 0

    # zero out crosslistings and same titles, so only one rep for each
    # crosslisting
    covered_ids = set()
    for i in xrange(psarray.shape[1]):
        if i in covered_ids:
            continue
        course_id = course_ids[i]
        course = Course.objects.get(id=course_id)
        for xlist_course in list(chain(
                course.crosslisted_courses.all(),
                Course.objects.filter(title=course.title))):
            if xlist_course == course:
                continue
            if xlist_course.id in reverse_course_ids:
                xlist_col = reverse_course_ids[xlist_course.id]
                if xlist_course not in covered_ids:
                    psarray[:, xlist_col] = 0
                    covered_ids.add(xlist_col)
        covered_ids.add(i)

    recommendations_to_create = []
    for i in xrange(psarray.shape[0]):
        current_class = Course.objects.get(id=course_ids[i])

        # zero out the diagonal
        zero_ids = [i]

        # zero out crosslisted classes
        zero_ids += current_class.crosslisted_courses.values_list(
            "id", flat=True)

        # zero out classes with the same title
        zero_ids += Course.objects.filter(
            title=current_class.title).values_list("id", flat=True)

        for zero_id in zero_ids:
            if zero_id in reverse_course_ids:
                psarray[i, reverse_course_ids[zero_id]] = 0

        for other_i in np.argpartition(
                psarray[i, :],
                -RECOMMENDATIONS_PER_CLASS)[-RECOMMENDATIONS_PER_CLASS:]:
            course_id = course_ids[other_i]

            # print "{} {} -> {}".format(
            #     psarray[i, other_i], current_class,
            #     Course.objects.get(id=course_id))

            recommendations_to_create.append(Recommendation(
                course=current_class,
                recommendation_id=course_id,
                creator=Recommendation.DOCUMENT_SIMILARITY,
                weight=psarray[i, other_i]
            ))

    with transaction.atomic():
        Recommendation.objects.filter(
            creator=Recommendation.DOCUMENT_SIMILARITY).delete()
        Recommendation.objects.bulk_create(recommendations_to_create)

    print "finished in {}".format(time() - t0)


def _clean_text_to_raw_words(text):
    if text:
        return " ".join([
            w for w in re.sub("[^a-zA-Z ]", "", text).lower().split()
            if len(w) > 3])
    else:
        return ""
