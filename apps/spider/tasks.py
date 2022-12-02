from celery import shared_task

from django.db import transaction

from apps.spider.crawlers import medians, orc, timetable
from apps.spider.models import CrawledData

from lib import task_utils
from lib.constants import CURRENT_TERM
from lib.terms import get_next_term


@shared_task
@task_utils.email_if_fails
@transaction.atomic
def import_pending_crawled_data(crawled_data_pk):
    crawled_data = CrawledData.objects.select_for_update().get(
        pk=crawled_data_pk)
    if crawled_data.data_type == CrawledData.MEDIANS:
        medians.import_medians(crawled_data.pending_data)
    elif crawled_data.data_type == CrawledData.ORC_DEPARTMENT_COURSES:
        orc.import_department(crawled_data.pending_data)
    else:
        assert crawled_data.data_type == CrawledData.COURSE_TIMETABLE
        timetable.import_timetable(crawled_data.pending_data)
    crawled_data.current_data = crawled_data.pending_data
    crawled_data.save()


@shared_task
@task_utils.email_if_fails
def crawl_medians():
    median_page_urls = medians.crawl_median_page_urls()
    if CURRENT_TERM == "22W":
        assert len(median_page_urls) == 8 # special case for 22W, which only has 8 medians
    assert len(median_page_urls) == 10 # the registrar medians web page always keeps a list links to the past ten academic terms
    for url in median_page_urls:
        crawl_term_median_page.delay(url)
    return median_page_urls


@shared_task
@task_utils.email_if_fails
def crawl_term_median_page(url):
    new_data = medians.crawl_term_medians_for_url(url)
    resource_name = "{term}_medians".format(
        term=medians.get_term_from_median_page_url(url),
    )
    return CrawledData.objects.handle_new_crawled_data(
        new_data, resource_name, CrawledData.MEDIANS)


@shared_task
@task_utils.email_if_fails
def crawl_orc():
    crawl_program_url.delay(orc.SUPPLEMENT_URL, "supplement")
    program_urls = orc.crawl_program_urls()
    assert len(program_urls) > 50
    for url in program_urls:
        crawl_program_url.delay(url)
    return sorted(program_urls)


@shared_task
@task_utils.email_if_fails
def crawl_program_url(url, program_code=None):
    if not program_code:
        program_code = url.split("/")[-1].split("-")[0]
        assert program_code.isupper() and len(program_code) in (3, 4)
    resource_name = "{program_code}_{education_level_code}_courses".format(
        program_code=program_code.lower(),
        education_level_code=orc.get_education_level_code(url),
    )
    new_data = orc.crawl_courses_from_program_page_url(url, program_code)
    return CrawledData.objects.handle_new_crawled_data(
        new_data, resource_name, CrawledData.ORC_DEPARTMENT_COURSES)


@shared_task
@task_utils.email_if_fails
def crawl_timetable():
    resource_name_fmt = "{term}_timetable"

    # Crawl CURRENT_TERM
    new_data = timetable.crawl_timetable(CURRENT_TERM)
    CrawledData.objects.handle_new_crawled_data(
        new_data,
        resource_name_fmt.format(term=CURRENT_TERM.upper()),
        CrawledData.COURSE_TIMETABLE,
    )

    # Crawl next term
    # Since we are crawling the next term, we may get a couple course
    # listings before the course offerings are actually posted, so we only
    # act if there are more than 10 entries.
    next_term = get_next_term(CURRENT_TERM)
    new_data = timetable.crawl_timetable(next_term)
    if new_data and len(new_data) > 10:
        CrawledData.objects.handle_new_crawled_data(
            new_data,
            resource_name_fmt.format(term=next_term.upper()),
            CrawledData.COURSE_TIMETABLE,
        )
