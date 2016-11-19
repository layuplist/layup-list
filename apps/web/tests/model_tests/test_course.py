from django.test import TestCase
from apps.web.models import Course, CourseOffering
from apps.web.tests import factories


class CourseTestCase(TestCase):
    TEST_TERM = "16W"

    def setUp(self):
        self.distrib = factories.DistributiveRequirementFactory()
        self.c1 = factories.CourseFactory()
        self.c2 = factories.CourseFactory()
        self.c1o = factories.CourseOfferingFactory(
            term=self.TEST_TERM, course=self.c1)
        self.c2o = factories.CourseOfferingFactory(
            term=self.TEST_TERM, course=self.c2)

    def test_for_term_retrieves_courses_for_term(self):
        self.assertEqual(len(Course.objects.for_term(self.TEST_TERM)), 2)
        CourseOffering.objects.all().delete()
        self.assertEqual(len(Course.objects.for_term(self.TEST_TERM)), 0)

    def test_for_term_filters_by_distrib_correctly(self):
        self.assertEqual(len(Course.objects.for_term(
            self.TEST_TERM, self.distrib.name)), 0)
        self.c1.distribs.add(self.distrib)
        self.c1.save()
        self.assertEqual(len(Course.objects.for_term(
            self.TEST_TERM, self.distrib.name)), 1)

    def test_review_search_retrieves_review_by_comments(self):
        c1r = factories.ReviewFactory(
            course=self.c1, comments="this class was not very good")
        self.assertEqual(self.c1.search_reviews("CLASS")[0], c1r)
        self.assertEqual(len(self.c1.search_reviews("asdf")), 0)

    def test_review_search_retrieves_review_by_professor(self):
        c1r = factories.ReviewFactory(course=self.c1, professor="Layup List")
        self.assertEqual(self.c1.search_reviews("layup")[0], c1r)
        self.assertEqual(len(self.c1.search_reviews("easy")), 0)

    def test_review_search_retrieves_review_by_both_comments_and_professor(
            self):
        factories.ReviewFactory(
            course=self.c1, comments="this class is a layup")
        factories.ReviewFactory(course=self.c1, professor="Layup List")
        self.assertEqual(len(self.c1.search_reviews("lay")), 2)

    def test_is_offered_returns_true_if_offered_on_specified_term(self):
        self.assertTrue(self.c1.is_offered(self.TEST_TERM))
        self.c1o.term = "00X"
        self.c1o.save()
        self.assertFalse(self.c1.is_offered(self.TEST_TERM))

    def test_offered_times_retrieves_times_offered_for_term(self):
        offered_times = ("2A", "3B")
        self.c1o.period, self.c2o.period = offered_times
        self.c2o.course = self.c1
        self.c1o.save()
        self.c2o.save()
        times = self.c1.offered_times(self.TEST_TERM)
        self.assertEqual(len(times), len(offered_times))
        for time in times:
            self.assertTrue(time in offered_times)

    def test_offered_times_ignores_duplicates(self):
        offered_time = "2A"
        self.c1o.period, self.c2o.period = offered_time, offered_time
        self.c2o.course = self.c1
        self.c1o.save()
        self.c2o.save()
        times = self.c1.offered_times(self.TEST_TERM)
        self.assertEqual(len(times), 1)
        self.assertEqual(times[0], offered_time)

    def test_offered_times_redacts_unordinary_times(self):
        offered_times = ("2A", "F 4:00 PM-6:00 PM")
        self.c1o.period, self.c2o.period = offered_times
        self.c2o.course = self.c1
        self.c1o.save()
        self.c2o.save()
        times = self.c1.offered_times(self.TEST_TERM)
        self.assertEqual(len(times), len(offered_times))
        for time in times:
            self.assertTrue(time in offered_times or time == "other")
        self.assertTrue("other" in times)


class CourseSearchTestCase(TestCase):
    DEPARTMENT_4 = "COSC"
    DEPARTMENT_3 = "REL"

    def setUp(self):
        self.c1 = factories.CourseFactory(
            department=self.DEPARTMENT_4, number=1)
        self.c2 = factories.CourseFactory(
            department=self.DEPARTMENT_4, number=2)
        self.c3 = factories.CourseFactory(
            department=self.DEPARTMENT_3, number=3)
        self.c4 = factories.CourseFactory(
            department=self.DEPARTMENT_3, number=4)

    def test_search_returns_nothing_if_no_query(self):
        self.assertEqual(len(Course.objects.search("")), 0)

    def test_searches_by_four_letter_department(self):
        # e.g. HIST
        self.c4.title = "something something {}".format(self.DEPARTMENT_4)
        self.c4.save()
        self.assertEqual(len(Course.objects.search(self.DEPARTMENT_4)), 2)

    def test_searches_by_three_letter_department(self):
        # e.g. REL
        self.c2.title = "something something {}".format(self.DEPARTMENT_3)
        self.c2.save()
        self.assertEqual(len(Course.objects.search(self.DEPARTMENT_3)), 2)

    def test_searches_as_query_if_dpt_length_but_not_valid_department(self):
        # e.g. war, boom
        self.c1.title = "the art of war"
        self.c2.title = "World War II"
        self.c1.save()
        self.c2.save()
        self.assertEqual(len(Course.objects.search("war")), 2)

        self.c1.title = "the art of boomerangs"
        self.c2.title = "World BOOM II"
        self.c1.save()
        self.c2.save()
        self.assertEqual(len(Course.objects.search("war")), 0)
        self.assertEqual(len(Course.objects.search("boom")), 2)

    def test_searches_by_number_and_subnumber(self):
        # e.g. COSC 089.01, COSC089.01
        self.assertEqual(len(Course.objects.search(
            "{}1.5".format(self.DEPARTMENT_4))), 0)
        self.assertEqual(len(Course.objects.search(
            "{} 1.5".format(self.DEPARTMENT_4))), 0)
        self.c1.subnumber = 5
        self.c1.save()
        self.assertEqual(len(Course.objects.search(
            "{}1.5".format(self.DEPARTMENT_4))), 1)
        self.assertEqual(len(Course.objects.search(
            "{} 1.5".format(self.DEPARTMENT_4))), 1)

    def test_searches_by_number_and_no_subnumber(self):
        # e.g. COSC 1
        self.assertEqual(len(Course.objects.search(
            "{}1".format(self.DEPARTMENT_4))), 1)
        self.assertEqual(len(Course.objects.search(
            "{} 1".format(self.DEPARTMENT_4))), 1)
        self.c1.delete()
        self.assertEqual(len(Course.objects.search(
            "{}1".format(self.DEPARTMENT_4))), 0)
        self.assertEqual(len(Course.objects.search(
            "{} 1".format(self.DEPARTMENT_4))), 0)

    def test_search_is_case_insensitive(self):
        self.c1.title = "The Art of War"
        self.c1.save()
        self.assertEqual(len(Course.objects.search("art of war")), 1)
