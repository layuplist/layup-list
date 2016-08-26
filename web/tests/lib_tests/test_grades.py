from django.test import TestCase
from lib import grades


class GradesTestCase(TestCase):

    def test_numeric_value_for_grade_retrieves_single_letter_grades(self):
        for grade, value in grades.GRADE_MAPPINGS.iteritems():
            self.assertEqual(grades.numeric_value_for_grade(grade), value)

    def test_numeric_value_for_grade_handles_in_between_grades(self):
        self.assertEqual(grades.numeric_value_for_grade(
            'A/A-'), (11.0 + 12.0) / 2)
        self.assertEqual(grades.numeric_value_for_grade(
            'A-/B+'), (10.0 + 11.0) / 2)
        self.assertEqual(grades.numeric_value_for_grade(
            'B+/B'), (9.0 + 10.0) / 2)
        self.assertEqual(grades.numeric_value_for_grade(
            'B/B-'), (8.0 + 9.0) / 2)
        self.assertEqual(grades.numeric_value_for_grade(
            'B-/C+'), (7.0 + 8.0) / 2)
        self.assertEqual(grades.numeric_value_for_grade(
            'C+/C'), (6.0 + 7.0) / 2)
        self.assertEqual(grades.numeric_value_for_grade(
            'C/C-'), (5.0 + 6.0) / 2)
        self.assertEqual(grades.numeric_value_for_grade(
            'C-/D'), (3.0 + 5.0) / 2)
        self.assertEqual(grades.numeric_value_for_grade(
            'D/E'), (0.0 + 3.0) / 2)
