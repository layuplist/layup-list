from layup_list.celery import app
from apps.spider.models import CrawledData
from apps.spider.tasks import crawl_medians, crawl_orc, crawl_timetable


def crawl_and_import_data(include_orc=False):
    old_task_always_eager = app.conf.task_always_eager
    app.conf.task_always_eager = True

    # ORC crawling takes a long time, especially when run synchronously.
    # If the ORC is not crawled, the course selection will only be limited,
    # but this should not interfere with development
    if include_orc:
        print "Crawling ORC. This will take a while."
        crawl_orc()
    else:
        print "Skipping ORC crawling. Should be enough for development."

    print "Crawling timetable"
    crawl_timetable()

    print "Crawling medians"
    crawl_medians()

    if include_orc:
        print "Importing ORC"
        _import_crawled_datas(CrawledData.ORC_DEPARTMENT_COURSES)

    print "Importing timetable"
    _import_crawled_datas(CrawledData.COURSE_TIMETABLE)

    print "Importing medians"
    _import_crawled_datas(CrawledData.MEDIANS)

    app.conf.task_always_eager = old_task_always_eager


def _import_crawled_datas(data_type):
    for crawled_data in CrawledData.objects.filter(data_type=data_type):
        if crawled_data.has_change():
            crawled_data.approve_change()
