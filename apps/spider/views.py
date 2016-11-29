from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import F
from django.shortcuts import redirect, render

from apps.spider.models import CrawledData


@staff_member_required
@user_passes_test(lambda u: u.is_superuser)
def crawled_data_list(request):
    if request.method == 'POST':
        for crawled_data in CrawledData.objects.all():
            if crawled_data.has_change():
                crawled_data.approve_change()
    return render(request, "crawled_data_list.html", {
        "crawled_datas": CrawledData.objects.pending_first(),
    })


@staff_member_required
@user_passes_test(lambda u: u.is_superuser)
def crawled_data_detail(request, crawled_data_pk):
    crawled_data = CrawledData.objects.get(pk=crawled_data_pk)
    if request.method == 'POST':
        crawled_data.approve_change()
        return redirect("crawled_datas")
    return render(request, "crawled_data_detail.html", {
        "crawled_data": crawled_data,
    })
