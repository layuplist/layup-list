from datetime import datetime
import re
from urllib2 import urlparse

from web.models import Course
from spider.utils import clean_department_code, retrieve_soup


BASE_URL = "http://dartmouth.smartcatalogiq.com/"
ORC_BASE_URL = urlparse.urljoin(BASE_URL, "/en/current/orc/")
ORC_UNDERGRAD_SUFFIX = "Departments-Programs-Undergraduate"
ORC_GRADUATE_SUFFIX = "Departments-Programs-Graduate"
UNDERGRAD_URL = urlparse.urljoin(ORC_BASE_URL, ORC_UNDERGRAD_SUFFIX)
GRADUATE_URL = urlparse.urljoin(ORC_BASE_URL, ORC_GRADUATE_SUFFIX)
INSTRUCTOR_TERM_REGEX = re.compile("^(?P<name>\w*)\s?(\((?P<term>\w*)\))?")

SUPPLEMENT_URL = (
    "http://dartmouth.smartcatalogiq.com/en/2016s/Supplement/Courses")

COURSE_HEADING_CORRECTIONS = {
    "COLT": {"7 First Year Seminars": "COLT 7 First Year Seminars"},
    "GRK": {"GRK 1.02-3.02 Intensive Greek": "GRK 1.02 Intensive Greek"},
    "INTS": {
        "INTS INTS 17.04 Migration Stories": "INTS 17.04 Migration Stories",
    },
    "MALS": {
        "MALS MALS 368 Seeing and Feeling in Early Modern Europe": (
            "MALS 368 Seeing and Feeling in Early Modern Europe"),
    },
}


def crawl_program_urls():
    programs = set()
    for orc_url in [UNDERGRAD_URL, GRADUATE_URL]:
        department_urls = _get_department_urls_from_url(orc_url)
        for department_url in department_urls:
            programs |= _get_program_urls_from_department_url(department_url)
    return programs


def _get_department_urls_from_url(url):
    soup = retrieve_soup(url)
    linked_urls = [
        urlparse.urljoin(BASE_URL, a["href"])
        for a in soup.find_all("a", href=True)
    ]
    return set(
        linked_url
        for linked_url in linked_urls
        if _is_department_url(linked_url, url)
    )


def _is_department_url(candidate_url, base_url):
    return (
        candidate_url.startswith(ORC_BASE_URL) and
        len(candidate_url) > len(base_url) and
        candidate_url.startswith(base_url) and
        "/" not in candidate_url[len(base_url) + 1:]
    )


def _get_program_urls_from_department_url(url):
    soup = retrieve_soup(url)
    linked_urls = [
        urlparse.urljoin(BASE_URL, a["href"])
        for a in soup.find_all("a", href=True)
    ]
    program_urls = set()
    for potential_program_url in linked_urls:
        if _is_course_url(potential_program_url):
            potential_program_url = (
                "/".join(potential_program_url.split("/")[:-1]))
        if _is_program_url(potential_program_url, url):
            program_urls.add(potential_program_url)
    return program_urls


def _is_program_url(candidate_url, department_url):
    top_directory_words = candidate_url.split("/")[-1].split("-")
    potential_department_name = top_directory_words[0]
    return (
        candidate_url.startswith(ORC_BASE_URL) and
        all(word.isalpha() for word in top_directory_words) and
        len(potential_department_name) in [3, 4] and
        potential_department_name.isupper() and
        not _is_course_url(candidate_url)
    )


def crawl_courses_from_program_page_url(url, program_code):
    soup = retrieve_soup(url)
    linked_urls = [
        urlparse.urljoin(BASE_URL, a["href"])
        for a in soup.find_all("a", href=True)
    ]
    course_urls = sorted(
        set(url for url in linked_urls if _is_course_url(url)))
    return [
        _crawl_course_data(course_url, program_code)
        for course_url in course_urls
    ]


def _is_course_url(candidate_url):
    potential_course_data = candidate_url.split("/")[-1].split("-")
    return (
        len(potential_course_data) in (2, 3) and
        len(potential_course_data[0]) in (3, 4) and
        potential_course_data[0].isupper() and
        all(
            potential_number.isdigit()
            for potential_number in potential_course_data[1:]
        )
    )


def _crawl_course_data(course_url, program_code):
    soup = retrieve_soup(course_url)
    course_heading = " ".join(soup.find("h1").get_text().split())
    course_heading = COURSE_HEADING_CORRECTIONS.get(program_code, {}).get(
        course_heading, course_heading)
    split_course_heading = course_heading.split()
    department = split_course_heading[0]
    numbers = split_course_heading[1].split(".")
    if len(numbers) == 2:
        course_number, course_subnumber = (int(n) for n in numbers)
    else:
        assert len(numbers) == 1, course_url
        course_number, course_subnumber = int(numbers[0]), None
    course_title = " ".join(split_course_heading[2:])
    description = soup.find(class_="desc").get_text(strip=True)
    return {
        "department": department,
        "description": description,
        "number": course_number,
        "subnumber": course_subnumber,
        "title": course_title,
        "url": course_url,
    }


def get_education_level_code(url):
    if url.startswith(UNDERGRAD_URL) or url == SUPPLEMENT_URL:
        return "ug"
    else:
        assert url.startswith(GRADUATE_URL)
        return "gr"


def import_department(department_data):
    for course_data in department_data:
        Course.objects.update_or_create(
            department=course_data["department"],
            description=course_data["description"],
            number=course_data["number"],
            subnumber=course_data["subnumber"],
            defaults={
                "title": course_data["title"],
                "url": course_data["url"],
                "source": Course.SOURCES.ORC,
            },
        )
