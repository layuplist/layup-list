from django.shortcuts import render

def current_term(request):
    return render(request, 'current_term.html', {
        'page_javascript': 'LayupList.Web.CurrentTerm()'
    })
