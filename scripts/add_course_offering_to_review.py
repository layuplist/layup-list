from __future__ import division, print_function

import os
import json
import psycopg2

from collections import namedtuple
from psycopg2.extras import NamedTupleCursor


SELECT_INSTRUCTORS = """
    WITH matches AS (
    SELECT web_review.id AS r_id,
        professor,
        web_instructor.name,
        web_instructor.id AS i_id
    FROM web_review
    INNER JOIN web_instructor
    ON name LIKE SUBSTRING(professor, 0, length(professor)) || '%'
    WHERE professor != ''
    )
    SELECT matches.r_id, matches.i_id FROM (
        SELECT matches.r_id,
            professor,
            COUNT(matches.r_id) AS cnt
        FROM matches
        GROUP BY matches.r_id, professor) AS uniq
    INNER JOIN matches
    ON matches.r_id = uniq.r_id
    WHERE cnt = 1
"""

SELECT_REVIEWS = """
    SELECT id, course_id AS c_id, term
    FROM web_review;
"""

SELECT_COURSE_OFFERINGS = """
    SELECT *
    FROM web_courseoffering;
"""

SELECT_COURSE_OFFERING = """
    SELECT id
    FROM web_courseoffering
    WHERE course_id = %(course_id)s AND term = %(term)s AND period = '';
"""

INSERT_COURSE_OFFERING = """
    INSERT INTO web_courseoffering (course_id, term, section, period, created_at, updated_at)
    VALUES (%(c_id)s, %(term)s, %(section)s, %(period)s, now(), now())
    RETURNING id;
"""


INSERT_CO_INSTRUCTORS = """
    INSERT INTO web_courseoffering_instructors (courseoffering_id, instructor_id)
    VALUES (%(co_id)s, %(i_id)s)
    RETURNING id;
"""

UPDATE_REVIEW = """
    UPDATE web_review
    SET course_offering_id = (%(co_id)s)
    WHERE id = (%(review_id)s)
    RETURNING id;
"""


def select(cur, query, params=None):
    cur.execute(query, params)
    return cur


def insert(cur, query, params=None):
    cur.execute(query, params)
    return cur.fetchone()[0]  # id of just inserted


def update(cur, query, params=None):
    cur.execute(query, params)
    return cur.fetchone()[0]  # id of just inserted


def create_review_to_instructor_mapping(cur):
    """Returns a mapping from review to instructor for those reviews with a
    `professor` field that uniquely matches an instructor name

    *Important note*: this is not guaranteed to be accurate!

    The following is an example where this function can be wrong: Prof. Jane
    Austen taught ENGL 1 in 2001, but has left Dartmouth. Prof Jane Albrecht
    joined in 2005 and teaches HIST 1. This query will match Jane Albrecht to
    Jane A. as the professor who taught ENGL 1 in 2001.

    This issue mainly applies to old reviews for which we only have the data
    [First Name] + [Last Initial]. Can potentially be made better by doing dept
    checks (but doesn't seem worth it).
    """
    rows = select(cur, SELECT_INSTRUCTORS)
    return {row.r_id: row.i_id for row in rows}


def main():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    review_to_instructor_mapping = create_review_to_instructor_mapping(cur)

    cos = {(row.course_id, row.term)
           for row in select(cur, SELECT_COURSE_OFFERINGS)}
    new_course_offering_ids = []
    new_course_offering_to_instructor_ids = []
    updated_review_ids = []
    reviews = select(cur, SELECT_REVIEWS).fetchall()
    for review in reviews:
        if review.id not in review_to_instructor_mapping:
            continue

        print("*********")
        print("[review id]", review.id)
        if (review.c_id, review.term) not in cos:
            print("[adding new row to course offering]", review.c_id, review.term)
            params = {"c_id": review.c_id, "term": review.term, "section": 1, "period": ""}
            new_co_id = insert(cur, INSERT_COURSE_OFFERING, params)
            print("[new_co_id]", new_co_id)
            new_course_offering_ids.append(new_co_id)
            cos.add((review.c_id, review.term))

            instructor_id = review_to_instructor_mapping[review.id]
            print("[adding new row to co_to_instructor]", instructor_id)
            params = {"co_id": new_co_id, "i_id": instructor_id}
            new_co_to_i_id = insert(cur, INSERT_CO_INSTRUCTORS, params)
            print("[new_co_to_i_id]", new_co_to_i_id)
            new_course_offering_to_instructor_ids.append(new_co_to_i_id)

            co_id = new_co_id
        else:
            params = {"course_id": review.c_id, "term": review.term}
            co_id = select(cur, SELECT_COURSE_OFFERING, params).fetchone().id

        params = {"co_id": co_id, "review_id": review.id}
        print("[updating review's course offering]", review.id, co_id)
        updated_review_id = update(cur, UPDATE_REVIEW, params)
        updated_review_ids.append(updated_review_id)

    blob = {"new_course_offering_ids": new_course_offering_ids,
            "new_co_to_i_id": new_course_offering_to_instructor_ids,
            "updated_review_ids": updated_review_ids}

    with open("blob.json", "w") as blob_file:
        json.dump(blob, blob_file)


if __name__ == '__main__':
    main()
