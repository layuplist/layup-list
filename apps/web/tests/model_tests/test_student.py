from django.test import TestCase
from apps.web.models import Review, Student, Vote
from apps.web.tests import factories
from datetime import datetime
from lib import constants


class StudentTestCase(TestCase):

    def test_is_valid_dartmouth_student_email_only_allows_dartmouth(self):
        self.assertFalse(
            Student.objects.is_valid_dartmouth_student_email(
                'layuplist@gmail.com')
        )
        self.assertTrue(
            Student.objects.is_valid_dartmouth_student_email(
                'layuplist.16@dartmouth.edu')
        )

    def test_is_valid_dartmouth_student_email_allows_four_years_from_now(self):
        self.assertTrue(
            Student.objects.is_valid_dartmouth_student_email(
                'layuplist.{}@dartmouth.edu'.format(
                    str(datetime.now().year + 5)[2:]))
        )

    def test_is_valid_dartmouth_student_email_allows_dual_degree(self):
        self.assertTrue(
            Student.objects.is_valid_dartmouth_student_email(
                'layuplist.ug@dartmouth.edu')
        )
        self.assertTrue(
            Student.objects.is_valid_dartmouth_student_email(
                'layuplist.UG@dartmouth.edu')
        )

    def test_is_valid_dartmouth_student_email_forbids_alum(self):
        self.assertFalse(
            Student.objects.is_valid_dartmouth_student_email(
                'layuplist.16@alumni.dartmouth.edu')
        )

    def test_can_see_recommendations(self):
        s = factories.StudentFactory()
        self.assertFalse(s.can_see_recommendations())

        # create sufficient votes of wrong type
        for _ in xrange(constants.REC_UPVOTE_REQ):
            factories.VoteFactory(
                user=s.user, category=Vote.CATEGORIES.LAYUP, value=1)
            for value in [-1, 0]:
                for category in [c[0] for c in Vote.CATEGORIES.CHOICES]:
                    factories.VoteFactory(
                        user=s.user, category=category, value=value)

        # cannot view if does not reach vote count
        Vote.objects.all().delete()
        factories.ReviewFactory(user=s.user)
        for _ in xrange(constants.REC_UPVOTE_REQ - 1):
            factories.VoteFactory(
                user=s.user, category=Vote.CATEGORIES.GOOD, value=1)
            self.assertFalse(s.can_see_recommendations())

        # can view
        factories.VoteFactory(
            user=s.user, category=Vote.CATEGORIES.GOOD, value=1)
        self.assertTrue(s.can_see_recommendations())
