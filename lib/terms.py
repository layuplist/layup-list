import re

term_regex = re.compile("^(?P<year>[0-9]{2})(?P<term>[WSXFwsxf])$")

def numeric_value_of_term(term):
    term_data = term_regex.match(term)
    if term_data and term_data.group("year") and term_data.group("term"):
        year = int(term_data.group("year"))
        term = term_data.group("term")
        return year * 10 + {'w': 1, 's': 2, 'x': 3, 'f': 4}[term.lower()]
    return 0
