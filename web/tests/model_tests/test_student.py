from django.test import TestCase
from web.models import Student
from web.tests import factories
from datetime import datetime

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
                'layuplist.{}@dartmouth.edu'.format(str(datetime.now().year + 5)[2:]))
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
