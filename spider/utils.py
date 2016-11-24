from bs4 import BeautifulSoup
import HTMLParser
import json
import urllib2

html_parser = HTMLParser.HTMLParser()

DEPARTMENT_CORRECTIONS = {
    "M&SS": "QSS",
    "WGST": "WGSS"
}


def clean_department_code(department):
    department = html_parser.unescape(department.strip()).upper()
    return (
        DEPARTMENT_CORRECTIONS[department]
        if department in DEPARTMENT_CORRECTIONS else department
    )


def int_or_none(string):
    return int(string) if string else None


def pretty_json(data):
    return json.dumps(
        data, sort_keys=True, indent=4, separators=(',', ': '))


def parse_number_and_subnumber(numbers_text):
    numbers = numbers_text.split(".")
    if len(numbers) == 2:
        return (int(n) for n in numbers)
    else:
        assert len(numbers) == 1
        return int(numbers[0]), None


def retrieve_soup(url, data=None, preprocess=lambda x: x):
    return BeautifulSoup(
        preprocess(urllib2.urlopen(url, data=data).read()), "html.parser")
