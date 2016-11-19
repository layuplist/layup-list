import sys
import urllib2
from bs4 import BeautifulSoup

from web.models import Course, CourseMedian
from spider.utils import clean_department_code, retrieve_soup

MEDIAN_PAGE_INDEX_URL = "http://www.dartmouth.edu/~reg/transcript/medians/"
MEDIANS_URL_FMT = (
    "http://www.dartmouth.edu/~reg/transcript/medians/{term}.html")


def get_term_from_median_page_url(url):
    return url.split("/")[-1].split(".")[0]


def crawl_median_page_urls():
    soup = retrieve_soup(MEDIAN_PAGE_INDEX_URL)
    return _retrieve_term_medians_urls_from_soup(soup)


def _retrieve_term_medians_urls_from_soup(soup):
    return [
        urllib2.urlparse.urljoin("http://www.dartmouth.edu", a["href"])
        for a in soup.find_all("a", href=True)
        if _is_term_page_url(a["href"])
    ]


def _is_term_page_url(url):
    term = get_term_from_median_page_url(url)
    return url == "/~reg/transcript/medians/{term}.html".format(term=term)


def crawl_term_medians_for_url(url):
    soup = retrieve_soup(url)
    table_rows = soup.find("table").find("tbody").findAll("tr")
    medians = [
        _convert_table_row_to_dict(table_row) for table_row in table_rows]
    medians.sort(cmp=_median_dict_sorter)
    return medians


def _median_dict_sorter(a, b):
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


def _convert_table_row_to_dict(table_row):
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


def import_medians(data):
    for median_data in data:
        import_median(median_data)


def import_median(median_data):
    department = clean_department_code(median_data["course"]["department"])
    number = int(median_data["course"]["number"])
    subnumber = median_data["course"].get("subnumber")
    if subnumber:
        subnumber = int(subnumber)

    try:
        course = Course.objects.get(
            department=department, number=number, subnumber=subnumber)
    except Course.DoesNotExist:
        print "Could not find course for {}{}.{}".format(
            department, number, subnumber)
        return

    section = int(median_data["section"])
    enrollment = int(median_data["enrollment"])
    median = median_data["median"].strip()
    term = median_data["term"].strip()

    median, _ = CourseMedian.objects.update_or_create(
        course=course,
        section=section,
        term=term,
        defaults={
            "enrollment": enrollment,
            "median": median,
            "term": term,
        },
    )
    return median
