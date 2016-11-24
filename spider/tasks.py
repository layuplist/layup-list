from celery import shared_task

from django.db import transaction

from spider.crawlers import medians, orc
from spider.models import CrawledData

from lib import task_utils


@shared_task
@task_utils.email_if_fails
@transaction.atomic
def import_pending_crawled_data(crawled_data_pk):
    crawled_data = CrawledData.objects.select_for_update().get(
        pk=crawled_data_pk)
    if crawled_data.data_type == CrawledData.MEDIANS:
        medians.import_medians(crawled_data.pending_data)
    else:
        assert crawled_data.data_type == CrawledData.ORC_DEPARTMENT_COURSES
        orc.import_department(crawled_data.pending_data)
    crawled_data.current_data = crawled_data.pending_data
    crawled_data.save()


@shared_task
@task_utils.email_if_fails
def crawl_medians():
    median_page_urls = medians.crawl_median_page_urls()
    assert len(median_page_urls) == 10
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
