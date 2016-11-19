from django.test import TestCase
from apps.web.models import Vote, Course
from apps.web.tests import factories


class VoteTestCase(TestCase):

    def test_vote(self):
        gv = factories.VoteFactory(category=Vote.CATEGORIES.QUALITY)
        lv = factories.VoteFactory(
            course=gv.course,
            user=gv.user,
            category=Vote.CATEGORIES.DIFFICULTY
        )
        c = gv.course
        u = gv.user

        # doesn't work if value > 1
        self.assertEqual((None, False,), Vote.objects.vote(
            5, c.id, Vote.CATEGORIES.DIFFICULTY, u))

        self.assertEqual(gv.value, 0)
        self.assertEqual(lv.value, 0)
        self.assertEqual(c.difficulty_score, 0)
        self.assertEqual(c.quality_score, 0)

        # can upvote and downvote
        self.assertEqual((1, False,), Vote.objects.vote(
            1, c.id, Vote.CATEGORIES.QUALITY, u.id))
        self.assertEqual((-1, False,), Vote.objects.vote(
            -1, c.id, Vote.CATEGORIES.DIFFICULTY, u.id))

        gv.refresh_from_db()
        lv.refresh_from_db()
        c.refresh_from_db()
        self.assertEqual(gv.value, 1)
        self.assertEqual(lv.value, -1)
        self.assertEqual(c.quality_score, 1)
        self.assertEqual(c.difficulty_score, -1)

        # can unvote
        self.assertEqual((0, True,), Vote.objects.vote(
            1, c.id, Vote.CATEGORIES.QUALITY, u.id))
        self.assertEqual((0, True,), Vote.objects.vote(
            -1, c.id, Vote.CATEGORIES.DIFFICULTY, u.id))

        gv.refresh_from_db()
        lv.refresh_from_db()
        c.refresh_from_db()
        self.assertEqual(gv.value, 0)
        self.assertEqual(lv.value, 0)
        self.assertEqual(c.quality_score, 0)
        self.assertEqual(c.difficulty_score, 0)

    def test_group_courses_with_votes(self):
        factories.CourseFactory()
        factories.CourseFactory()
        v = factories.VoteFactory()
        factories.CourseFactory()

        results = Vote.objects.group_courses_with_votes(
            Course.objects.all(),
            v.category,
            v.user,
        )

        self.assertEqual(4, len(results))
        for course, vote in results:
            if course == v.course:
                self.assertEqual(vote, v)
            else:
                self.assertEqual(vote, None)
