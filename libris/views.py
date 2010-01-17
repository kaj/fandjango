from fandjango.libris.models import *
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponse
from django.db.models import Count

def index(request):
    years = Issue.objects.order_by('year').distinct().values_list('year', flat=True)
    titles = Title.objects.order_by('title').all()
    refs = RefKey.objects.order_by('title').annotate(Count('episode')).all()
    return render_to_response('index.html', {'years': years,
                                             'titles': titles,
                                             'refs': refs})
def year(request, year):
    issues = Issue.objects.filter(year=year)
    return render_to_response('year.html', {'year': year, 'issues': issues})

def title(request, slug):
    title = get_object_or_404(Title, slug=slug)
    return render_to_response('title.html', {'title': title})

def refKey(request, slug):
    refkey = get_object_or_404(RefKey, slug=slug)
    titles = refkey.episode_set.order_by('publication').all()
    return render_to_response('refkey.html', {'refkey': refkey,
                                              'titles': titles})
