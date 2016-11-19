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


def pretty_json(data):
    return json.dumps(
        data, sort_keys=True, indent=4, separators=(',', ': '))


def retrieve_soup(url):
    return BeautifulSoup(urllib2.urlopen(url).read(), "html.parser")
