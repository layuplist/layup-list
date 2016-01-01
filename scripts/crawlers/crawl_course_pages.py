import json
import urllib2
import re
from bs4 import BeautifulSoup

ORC_COURSES_FILE = "data/orc_courses.json"
OUTFILE_NAME = "data/course_pages.json"
instructor_term_regex = re.compile("^(?P<name>\w*)\s?(\((?P<term>\w*)\))?")

def crawl_course_pages():
    with open(ORC_COURSES_FILE) as data_file:
        courses_to_crawl = json.load(data_file)
        export_data([crawl_course(course) for course in courses_to_crawl])

def crawl_course(course):
    print "crawling {}".format(course["url"])
    page_text = urllib2.urlopen(course["url"]).read()
    soup = BeautifulSoup(urllib2.urlopen(course["url"]).read(), "html.parser")
    course["description"] = parse_description(soup)
    course["instructors"] = parse_instructors(soup)
    course["offered"] = parse_terms_offered(soup)

    # COULD BE ADDED:
    # - distributives
    # - cross listings
    # - prerequisites

    return course

def parse_description(soup):
    return soup.find(class_="desc").get_text(strip=True)

def parse_instructors(soup):
    instructors_div = soup.find(id="instructor")
    if not instructors_div:
        return []
    instructors_strings = list(instructors_div.stripped_strings)
    if len(instructors_strings) <= 1:
        return []
    instructors_before_split = instructors_strings[1]
    splitter = " and " if " and " in instructors_before_split else ", "
    raw_instructors = instructors_before_split.split(splitter)
    return [parse_instructor_and_term(raw_instructor) for raw_instructor in raw_instructors]

def parse_instructor_and_term(raw_instructor):
    instructor = instructor_term_regex.match(raw_instructor).groupdict()
    if not instructor["term"]:
        del instructor["term"]
        return instructor

def parse_terms_offered(soup):
    offered_div = soup.find(id="offered")
    if not offered_div:
        return None
    offered_strings = list(offered_div.stripped_strings)
    if len(offered_strings) <= 1:
        return None
    return list(offered_div.stripped_strings)[1]

def export_data(data):
    with open(OUTFILE_NAME, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == '__main__':
    crawl_course_pages()
