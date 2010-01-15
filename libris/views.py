from fandjango.libris.models import *
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponse

def year(request, year):
    issues = Issue.objects.filter(year=year)
    return render_to_response('year.html', {'year': year, 'issues': issues})

#return HttpResponse(u', '.join(unicode(i) for i in issues), 'text/plain')
