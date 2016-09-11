"""Extracts median information from Dartmouth.

Example Usage:
 python crawl_medians.py 13s 13x 13f 14w 14s 14x 14f 15w 15s 15x

Available terms are shown on:
http://www.dartmouth.edu/~reg/transcript/medians/
"""
import sys
import json
import urllib2
from bs4 import BeautifulSoup
from urllib2 import HTTPError
from operator import attrgetter

MEDIANS_URL_FMT = (
    "http://www.dartmouth.edu/~reg/transcript/medians/{term}.html")

OUTFILE_FMT = "{term}_medians.json"


def median_dict_sorter(a, b):
    a_section, b_section = a["section"], b["section"]
    a, b = a["course"], b["course"]
    a_department, b_department = a["department"], b["department"]
    a_number, b_number = a["number"], b["number"]
    a_subnumber, b_subnumber = a.get("subnumber"), b.get("subnumber")
    if a_department == b_department:
        if a_number == b_number:
            if a_subnumber == b_subnumber:
                return int(a_section) - int(b_section)
            else:
                if a_subnumber is None:
                    return -1
                if b_subnumber is None:
                    return 1
                return int(a_subnumber) - int(b_subnumber)
        else:
            return int(a_number) - int(b_number)
    else:
        return -1 if a_department < b_department else 1


def crawl_medians_for_terms(terms):
    for term in terms:
        url = MEDIANS_URL_FMT.format(term=term)
        medians = crawl_medians_at_url(url)
        medians.sort(cmp=median_dict_sorter)
        export_medians_to_json(OUTFILE_FMT.format(term=term), medians)


def crawl_medians_at_url(url):
    medians = []
    soup = BeautifulSoup(urllib2.urlopen(url).read(), "html.parser")
    table_rows = soup.find("table").find("tbody").findAll("tr")
    return [
        convert_table_row_to_dict(table_row) for table_row in table_rows
    ]


def convert_table_row_to_dict(table_row):
    median_data = table_row.findAll("td")
    term = median_data[0].get_text(strip=True)
    course = median_data[1].get_text(strip=True)
    enrl = median_data[2].get_text(strip=True)
    median = median_data[3].get_text(strip=True)

    median_dict = {
        "term": term,
        "course": {
            "department": course.split("-")[0],
            "number": course.split("-")[1].split(".")[0],
        },
        "section": course.split("-")[2],
        "enrollment": enrl,
        "median": median,
    }

    if len(course.split("-")[1].split(".")) > 1:
        median_dict["course"]["subnumber"] = course.split("-")[1].split(".")[1]

    return median_dict


def export_medians_to_json(filename, medians):
    with open(filename, 'w') as outfile:
        json.dump(
            medians, outfile, sort_keys=True, indent=2, separators=(',', ': '))


if __name__ == "__main__":
    crawl_medians_for_terms(sys.argv[1:])
