from fandjango.libris.models import *
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponse
from django.db.models import Count, Min
from math import pow

def ctx(**kwargs):
    '''Utility function for getting a rendering context.'''
    props = { }
    props.update(kwargs)
    if 'pagetitle' not in props:
        props['pagetitle'] = u'Rasmus Fantomenindex'
    if 'headtitle' not in props:
        props['headtitle'] = u'%s - %s' % (props['pagetitle'], 'Fandjango')
    return props
    
def orderEpisodeQuery(query):
    '''Take a query for Episodes and make it ordered by first publication.'''
    return query.annotate(Min('publication__issue__year')).annotate(Min('publication__issue__number')).order_by('publication__issue__number__min').order_by('publication__issue__year__min')

def index(request):
    years = Issue.objects.order_by('year').distinct().values_list('year', flat=True)
    titles = Title.objects.order_by('title').annotate(Count('episode')).all()
    refs = RefKey.objects.order_by('title').filter(kind='X').annotate(Count('episode')).all()
    people = Creator.objects.order_by('name').annotate(Count('creativepart')).all()
    def weighted(tags, key):
        counts = sorted(tag.__getattribute__(key) for tag in tags)
        n = len(counts)
        for tag in tags:
            tag.weight = int(round(
                pow(10, float(counts.index(tag.__getattribute__(key))) / n)))
        return tags

    return render_to_response('index.html', {
        'pagetitle': 'Fantomenindex',
        'years': years,
        'titles': weighted(titles, 'episode__count'),
        'refs': weighted(refs, 'episode__count'),
        'people': weighted(people, 'creativepart__count')
    })

def getNavYears(year, n=2):
    years = list(Issue.objects.order_by('year').distinct().values_list('year', flat=True))
    i = years.index(int(year))
    return years[max(i-n,0):i+n+1]

def year(request, year):
    issues = get_list_or_404(Issue, year=year)
    for issue in issues:
        issue.contents = issue.publication_set.all()
        for p in issue.contents:
            if p.episode:
                p.episode.otherpub = p.episode.publication_set.exclude(issue=issue)
    return render_to_response('year.html', ctx(year=year, issues=issues,
                                               navyears=getNavYears(year),
                                               pagetitle='Fantomen %s' %(year)))

def title(request, slug):
    title = get_object_or_404(Title, slug=slug)
    episodes = orderEpisodeQuery(title.episode_set).all()
    return render_to_response('title.html', ctx(title=title, episodes=episodes,
                                                pagetitle=unicode(title)))

def refKey(request, slug):
    refkey = get_object_or_404(RefKey, slug=slug)
    episodes = orderEpisodeQuery(refkey.episode_set).all()
    articles = refkey.article_set.all()
    return render_to_response('refkey.html', ctx(refkey=refkey, 
                                                 episodes=episodes,
                                                 articles=articles,
                                                 pagetitle=unicode(refkey)))

def creator(request, slug):
    creator = get_object_or_404(Creator, slug=slug)
    q=CreativePart.objects.filter(creator=creator)
    episodes = orderEpisodeQuery(Episode.objects.filter(creativepart__in=q)).all()
    articles = () # refkey.article_set.all()
    return render_to_response('creator.html', ctx(creator=creator,
                                                  episodes=episodes,
                                                  articles=articles,
                                                  pagetitle=unicode(creator)))
