import re
from lib import constants

term_regex = re.compile("^(?P<year>[0-9]{2})(?P<term>[WSXFwsxf])$")


def numeric_value_of_term(term):
    term_data = term_regex.match(term)
    if term_data and term_data.group("year") and term_data.group("term"):
        year = int(term_data.group("year"))
        term = term_data.group("term")
        return year * 10 + {'w': 1, 's': 2, 'x': 3, 'f': 4}[term.lower()]
    return 0


def is_valid_term(term):
    term_data = term_regex.match(term)
    current_year = int(term_regex.match(constants.CURRENT_TERM).group("year"))
    return term_data and int(term_data.group("year")) <= current_year
