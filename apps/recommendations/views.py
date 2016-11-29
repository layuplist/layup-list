from django.shortcuts import render
from django.views.decorators.http import require_safe
from django.contrib.auth.decorators import login_required
from apps.recommendations.models import Recommendation
from lib import constants


@require_safe
@login_required
def recommendations(request):
    return render(request, 'recommendations.html', {
        'recommendations': Recommendation.objects.for_user(
            request.user, "show_all" in request.GET),
        'constants': constants
    })
