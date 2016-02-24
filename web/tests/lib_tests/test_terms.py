from django.test import TestCase
from lib import terms, constants
import random

class TermsTestCase(TestCase):

    def test_term_regex_works_in_common_case(self):
        term_data = terms.term_regex.match('16W')
        self.assertTrue(term_data and term_data.group('year') == '16' and term_data.group('term') == 'W')

    def test_term_regex_only_allows_two_digit_years(self):
        term_data = terms.term_regex.match('2016W')
        self.assertFalse(term_data)

    def test_term_regex_disallows_bad_terms(self):
        self.assertFalse(terms.term_regex.match('16a'))

    def test_term_regex_allows_for_lower_and_upper_terms(self):
        term_data = terms.term_regex.match('16W')
        self.assertTrue(term_data and term_data.group('year') == '16' and term_data.group('term') == 'W')
        term_data = terms.term_regex.match('16w')
        self.assertTrue(term_data and term_data.group('year') == '16' and term_data.group('term') == 'w')

    def test_term_regex_allows_for_current_term(self):
        term_data = terms.term_regex.match(constants.CURRENT_TERM)
        self.assertTrue(term_data and term_data.group('year') == constants.CURRENT_TERM[:2] and term_data.group('term') == constants.CURRENT_TERM[2])

    def test_numeric_value_of_term_returns_0_if_bad_term(self):
        self.assertEqual(terms.numeric_value_of_term(''), 0)
        self.assertEqual(terms.numeric_value_of_term('asd'), 0)
        self.assertEqual(terms.numeric_value_of_term('2001'), 0)
        self.assertEqual(terms.numeric_value_of_term('1s'), 0)
        self.assertEqual(terms.numeric_value_of_term('2016w'), 0)
        self.assertEqual(terms.numeric_value_of_term('fall'), 0)

    def test_numeric_value_of_term_ranks_terms_in_correct_order(self):
        correct_order = ['', '09w', '09S', '09X', '12F', '14x', '15W', '16S', '20x']
        shuffled_data = list(correct_order)
        while correct_order == shuffled_data:
            random.shuffle(shuffled_data)
        sorted_data = sorted(shuffled_data, key=lambda term: terms.numeric_value_of_term(term))
        self.assertNotEqual(correct_order, shuffled_data)
        self.assertEqual(correct_order, sorted_data)

    def test_numeric_value_of_term_gives_expected_numeric_value(self):
        self.assertEqual(terms.numeric_value_of_term('16W'), 161)

    def test_is_valid_term_returns_false_if_in_future(self):
        next_year = int(terms.term_regex.match(constants.CURRENT_TERM).group('year')) + 1
        self.assertFalse(terms.is_valid_term('{}f'.format(next_year)))

    def test_is_valid_term_returns_false_if_no_term(self):
        self.assertFalse(terms.is_valid_term(''))

    def test_is_valid_term_returns_false_if_no_year(self):
        self.assertFalse(terms.is_valid_term('w'))

    def test_is_valid_term_returns_true_for_current_term(self):
        self.assertTrue(terms.is_valid_term(constants.CURRENT_TERM))
