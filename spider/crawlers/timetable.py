import re

from django.db import transaction

from web.models import (
    Course,
    CourseOffering,
    DistributiveRequirement,
    Instructor,
)

from spider.utils import (
    int_or_none,
    parse_number_and_subnumber,
    retrieve_soup,
)
from lib.terms import split_term
from lib.constants import CURRENT_TERM

TIMETABLE_URL = (
    "http://oracle-www.dartmouth.edu/dart/groucho/timetable.display_courses")

DATA_TO_SEND = (
    "distribradio=alldistribs&depts=no_value&periods=no_value&"
    "distribs=no_value&distribs_i=no_value&distribs_wc=no_value&pmode=public&"
    "term=&levl=&fys=n&wrt=n&pe=n&review=n&crnl=no_value&classyear=2008&"
    "searchtype=Subject+Area%28s%29&termradio=selectterms&terms=no_value&"
    "subjectradio=selectsubjects&hoursradio=allhours&sortorder=dept"
    "&terms={term}"
)


def crawl_timetable(term):
    """
    Timetable HTML is malformed. All table rows except the head do not have
    a proper starting <tr>, which requires us to:

    1. Iterate over <td></td> in chunks rather than by <tr></tr>
    2. Remove all </tr> in the table, which otherwise breaks BeautifulSoup into
       not allowing us to iterate over all the <td></td>

    To iterate over the <td></td> in chunks, we get the number of columns,
    put all of the <td></td> in a generator, and pull the number of columns
    from the generator to get the row.
    """
    course_data = []
    request_data = DATA_TO_SEND.format(term=_get_timetable_term_code(term))
    soup = retrieve_soup(
        TIMETABLE_URL,
        data=request_data,
        preprocess=lambda x: re.sub("</tr>", "", x),
    )
    num_columns = len(soup.find(class_="data-table").find_all("th"))
    assert num_columns == 18

    tds = soup.find(class_="data-table").find_all("td")
    assert len(tds) % num_columns == 0

    td_generator = (td for td in tds)
    for _ in xrange(len(tds) / num_columns):
        tds = [next(td_generator) for _ in xrange(num_columns)]

        number, subnumber = parse_number_and_subnumber(tds[3].get_text())
        crosslisted_courses = _parse_crosslisted_courses(
            tds[7].get_text(strip=True))

        course_data.append({
            "term": _convert_timetable_term_to_term(
                tds[0].get_text(strip=True)),
            "crn": int(tds[1].get_text(strip=True)),
            "program": tds[2].get_text(strip=True),
            "number": number,
            "subnumber": subnumber,
            "section": int(tds[4].get_text(strip=True)),
            "title": tds[5].get_text(strip=True).encode(
                'ascii', 'ignore').decode('ascii'),
            "crosslisted": crosslisted_courses,
            "period": tds[8].get_text(strip=True),
            "room": tds[9].get_text(strip=True),
            "building": tds[10].get_text(strip=True),
            "instructor": _parse_instructors(tds[11].get_text(strip=True)),
            "world_culture": tds[12].get_text(strip=True),
            "distribs": _parse_distribs(tds[13].get_text(strip=True)),
            "limit": int_or_none(tds[14].get_text(strip=True)),
            # "enrollment": int_or_none(tds[15].get_text(strip=True)),
            "status": tds[16].get_text(strip=True),
        })
    return course_data


def _parse_crosslisted_courses(xlist_text):
    crosslisted_courses = []
    for course_text in (xlist_text.split(",") if xlist_text else []):
        program, numbers, section = course_text.split()
        number, subnumber = parse_number_and_subnumber(numbers)
        section = int(section)
        crosslisted_courses.append({
            "program": program,
            "number": number,
            "subnumber": subnumber,
            "section": section,
        })
    return crosslisted_courses


def _convert_timetable_term_to_term(timetable_term):
    assert len(timetable_term) == 6
    assert timetable_term[:2] == "20"
    month = int(timetable_term[-2:])
    year = timetable_term[2:4]
    return "{year}{season}".format(
        year=year, season={1: "W", 3: "S", 6: "X", 9: "F"}[month])


def _parse_distribs(distribs_text):
    return distribs_text.split(" or ") if distribs_text else []


def _parse_instructors(instructors):
    return instructors.split(", ") if instructors else []


def _get_timetable_term_code(term):
    year, term = split_term(term)
    return "20{year}0{term_number}".format(
        year=year,
        term_number={"w": 1, "s": 3, "x": 6, "f": 9}[term.lower()],
    )


def import_timetable(timetable_data):
    for course_data in timetable_data:
        _import_course_data(course_data)


@transaction.atomic
def _import_course_data(course_data):
    course = _get_or_import_course(course_data)
    offering = _update_or_import_offering(course_data, course)
    _update_crosslisted_courses(course_data, course)
    _update_distribs(course_data, course)
    _update_instructors(course_data, offering)


def _get_or_import_course(course_data):
    course, _ = Course.objects.get_or_create(
        department=course_data["program"],
        number=course_data["number"],
        subnumber=course_data["subnumber"],
        defaults={
            "title": course_data["title"],
            "source": Course.SOURCES.TIMETABLE,
        },
    )
    return course


def _update_or_import_offering(course_data, course):
    offering, _ = CourseOffering.objects.update_or_create(
        course=course,
        section=course_data["section"],
        term=course_data["term"],
        defaults={
            "course_registration_number": course_data["crn"],
            "period": course_data["period"],
            "limit": course_data["limit"],
        },
    )
    return offering


def _update_crosslisted_courses(course_data, course):
    crosslisted_courses_data = course_data["crosslisted"]
    for crosslisted_course_data in crosslisted_courses_data:
        # We ignore missing courses because they should be created later in the
        # timetable importing process.
        crosslisted_course = Course.objects.filter(
            department=crosslisted_course_data["program"],
            number=crosslisted_course_data["number"],
            subnumber=crosslisted_course_data["subnumber"],
        ).first()
        if crosslisted_course:
            course.crosslisted_courses.add(crosslisted_course)


def _update_distribs(course_data, course):
    for distrib_name in course_data["distribs"]:
        distrib, _ = DistributiveRequirement.objects.get_or_create(
            name=distrib_name,
            defaults={
                "distributive_type": DistributiveRequirement.DISTRIBUTIVE,
            },
        )
        course.distribs.add(distrib)

    if course_data["world_culture"]:
        distrib, _ = DistributiveRequirement.objects.get_or_create(
            name=course_data["world_culture"],
            defaults={
                "distributive_type": DistributiveRequirement.WORLD_CULTURE,
            },
        )
        course.distribs.add(distrib)


def _update_instructors(course_data, offering):
    for instructor_name in course_data["instructor"]:
        instructor, _ = Instructor.objects.get_or_create(
            name=instructor_name,
        )
        offering.instructors.add(instructor)
