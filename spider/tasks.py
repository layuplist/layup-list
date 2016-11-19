from celery import shared_task

from django.db import transaction

from spider.crawlers import medians
from spider.models import CrawledData

from lib import task_utils


@shared_task
@task_utils.email_if_fails
@transaction.atomic
def import_pending_crawled_data(crawled_data_pk):
    crawled_data = CrawledData.objects.select_for_update().get(
        pk=crawled_data_pk)
    assert crawled_data.data_type == crawled_data.MEDIANS
    medians.import_medians(crawled_data.pending_data)
    crawled_data.current_data = crawled_data.pending_data
    crawled_data.save()


@shared_task
@task_utils.email_if_fails
def crawl_medians():
    median_page_urls = medians.crawl_median_page_urls()
    assert (
        len(median_page_urls) == 10,
        "Unexpected number of median pages found ({})".format(
            len(median_page_urls)))
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
    db_data, created = CrawledData.objects.update_or_create(
        resource=resource_name,
        data_type=CrawledData.MEDIANS,
        defaults={"pending_data": new_data},
    )
    if created or db_data.has_change():
        db_data.request_change()
        return True
    return False
