# -*- encoding: utf-8; -*-
from django.core import urlresolvers
from django.conf import settings
from django.db.models import Count, F, Func, Min, Max
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.views.decorators.cache import cache_page
from django.views.defaults import page_not_found
from libris.models import *
from libris.alias import *
from math import pow
import re

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
    return query.annotate(sortno=Min('publication__issue__ordering')) \
                .order_by('sortno')

def allPhantoms():
    # The slug for a phantom is 1, 2, .. 9, 10, .. 17, 17.1, 18 etc
    # Order them numerically!
    return RefKey.objects.order_by(Func(F('slug'),
                                        template='%(expressions)s::numeric')) \
                 .filter(kind='F').annotate(Count('episode')).all()

@cache_page(60 * 15)
def autocomplete(request):
    q = request.GET.get('q')
    limit = 10
    hits = [{'t': h.title, 'u': '/%s' % h.slug, 'k': 't'}
            for h in Title.objects.filter(title__icontains=q)[:limit]]
    limit -= len(hits)
    if limit > 0:
        hits += [{'t': h.title, 'u': h.get_absolute_url(), 'k': h.kind.lower()}
                 for h in RefKey.objects.filter(title__icontains=q)
                                .exclude(kind__in=['T' ,'P'])[:limit]]
    limit -= len(hits)
    if limit > 0:
        hits += [{'t': h.name, 'u': h.get_absolute_url(), 'k': 'p'}
                 for h in Creator.objects.filter(name__icontains=q)[:limit]]
    return json_response(hits)

def json_response(data):
    import json
    return HttpResponse(json.dumps(data), content_type='application/json')

def search(request):
    query = request.GET.get('q', '')
    maxhits = 20
    from functools import reduce
    from operator import or_
    qs = Episode.objects
    titles = request.GET.getlist('t')
    for t in titles:
        qs = qs.filter(title__slug=t)
    phantoms = request.GET.getlist('f')
    for f in phantoms:
        qs = qs.filter(ref_keys__slug=f)
    refkeys = request.GET.getlist('x')
    for x in refkeys:
        qs = qs.filter(ref_keys__slug=x)
    people = request.GET.getlist('p')
    for p in people:
        qs = qs.filter(creativepart__creator__slug=p)
    lookups = ['episode', 'title__title', 'teaser', 'orig_name__title',
               'note', 'ref_keys__title', 'copyright']
    lookups = ["%s__icontains" % field for field in lookups]
    for bit in query.split():
        print("Filtering query for", bit)
        qs = qs.filter(reduce(or_,
                              [models.Q(**{lookup: bit})
                               for lookup in lookups]))
    episodes = orderEpisodeQuery(qs) \
        .select_related('title') \
        .select_related('orig_name') \
        .prefetch_related('creativepart_set__creator') \
        .prefetch_related('publication_set__issue') \
        .prefetch_related('ref_keys')
    c = episodes.count()
    if c > maxhits:
        episodes = episodes[:maxhits]
    else:
        episodes = episodes.all()
        maxhits = None
    return render_to_response('search.html', ctx(
        query=query,
        nhits=c,
        maxhits=maxhits,
        episodes=episodes,
        titles=Title.objects.filter(slug__in=titles),
        refkeys=RefKey.objects.filter(slug__in=refkeys),
        people=Creator.objects.filter(slug__in=people),
        phantoms=RefKey.objects.filter(slug__in=phantoms),
        pagetitle='Sök'))

def index(request):
    years = Issue.objects.order_by('year').distinct().values_list('year', flat=True)
    titles = Title.objects.order_by('title')
    refs = RefKey.objects.order_by('title').filter(kind='X')
    people = Creator.objects.order_by('name') \
                            .filter(creativepart__role__in=['', 'text', 'bild', 'ink'])
    def weighted(items, key, limit=1):
        items = items.annotate(cnt=Count(key)).filter(cnt__gt=limit).all()
        counts = sorted(item.cnt for item in items)
        n = len(counts)
        for i in items:
            i.weight = int(round(pow(10, float(counts.index(i.cnt)) / n)))
        return items

    return render_to_response('index.html', {
        'frontpage': True,
        'pagetitle': 'Rasmus Fantomenindex',
        'n_issues': Publication.objects.filter(ordno__lt=4711) \
                               .distinct().values_list('issue_id').count(),
        'years': years,
        'phantoms': allPhantoms(),
        'titles': weighted(titles, 'episode', 7),
        'refs': weighted(refs, 'episode', 4),
        'people': weighted(people, 'creativepart', 20),
    })

def titles(request):
    titles = Title.objects.order_by('title') \
        .annotate(first=Min('episode__publication__issue__year')) \
        .annotate(latest=Max('episode__publication__issue__year')) \
        .annotate(count=Count('episode')).all()
    return render_to_response('list.html', {
        'pagetitle': 'Serier i Fantomentidningen',
        'items': titles,
    })

def getNavYears(year, n=5):
    years = list(Issue.objects.order_by('year').distinct().values_list('year', flat=True))
    i = years.index(int(year))
    return years[max(i-n,0):i+n+1]

def year(request, year):
    issues = get_list_or_404(
        Issue.objects \
        .prefetch_related('publication_set__episode__title') \
        .prefetch_related('publication_set__episode__orig_name') \
        .prefetch_related('publication_set__episode__ref_keys') \
        .prefetch_related('publication_set__episode__creativepart_set__creator') \
        .prefetch_related('publication_set__episode__publication_set') \
        .prefetch_related('publication_set__episode__publication_set__issue') \
        .prefetch_related('publication_set__article__ref_keys') \
        .prefetch_related('publication_set__article__creators') \
        .prefetch_related('cover_by'),
        year=year)
    for issue in issues:
        issue.contents = issue.publication_set.all()
        for p in issue.contents:
            if p.episode:
                p.otherpub = [op for op in p.episode.publication_set.all()
                              if op.issue != issue]
    return render_to_response('year.html', ctx(year=int(year), issues=issues,
                                               navyears=getNavYears(year),
                                               pagetitle='Fantomen %s' %(year)))

DAYSTRIPS = {'fantomen', 'mandrake', 'rick_oshay', 'king_vid_granspolisen',
             'blixt_gordon', 'johnny_hazard', 'latigo'}
SUNDAYCOMICS = {'fantomen', 'mandrake', 'johnny_hazard'}

def title(request, slug, pagesize=200, strips=None):
    title = get_object_or_404(Title, slug=slug)
    episodes = title.episode_set
    if strips:
        episodes = episodes.filter(daystrip__is_sundays=(strips=='sun')) \
                           .order_by('daystrip__fromdate')
        pagetitle = u'%s %s' % (
            title, u'söndagssidor' if strips=='sun' else 'dagstrip')
    else:
        episodes = orderEpisodeQuery(episodes)
        pagetitle = str(title)
    episodes = episodes \
        .select_related('orig_name') \
        .prefetch_related('creativepart_set__creator') \
        .prefetch_related('publication_set__issue') \
        .prefetch_related('ref_keys') \
        .all()
    count = episodes.count()
    key = RefKey.objects.filter(kind='T', slug=slug).first()
    if key:
        articles = key.article_set.all()
    else:
        articles = None
    if count >= 2*pagesize:
        pages = range(1 + count // pagesize)
        page = int_or_404(request.GET.get('page', 0))
        episodes = episodes[page*pagesize:(page+1)*pagesize]
    else:
        pages = None

    return render_to_response('title.html', ctx(
        title=title, episodes=episodes,
        havestrips=title.slug in DAYSTRIPS,
        havesundays=title.slug in SUNDAYCOMICS,
        articles=articles,
        pagetitle=pagetitle,
        pages=pages))

def int_or_404(n):
    try:
        return int(n)
    except:
        raise Http404('Not an integer: %r' % n)


def refKey(request, slug):
    refkey = get_object_or_404(RefKey, slug=slug, kind__in=['F', 'X'])
    episodes = orderEpisodeQuery(refkey.episode_set) \
        .select_related('title') \
        .select_related('orig_name') \
        .prefetch_related('creativepart_set__creator') \
        .prefetch_related('publication_set__issue') \
        .prefetch_related('ref_keys') \
        .all()
    articles = refkey.article_set \
        .prefetch_related('publication_set__issue') \
        .prefetch_related('creators') \
        .all()
    return render_to_response('refkey.html', ctx(
        refkey=refkey, episodes=episodes, articles=articles,
        phantoms=allPhantoms() if refkey.kind=='F' else None,
        pagetitle=str(refkey)))

def refKeys(request):
    refkeys = RefKey.objects.filter(kind='X').order_by('title') \
        .annotate(first=Min('episode__publication__issue__year')) \
        .annotate(latest=Max('episode__publication__issue__year')) \
        .annotate(count=Count('episode')).all()
    return render_to_response('list.html', {
        'pagetitle': u'Personer, platser och företeelser i Fantomens värld',
        'items': refkeys,
    })

def creator(request, slug):
    creator = get_object_or_404(Creator, slug=slug)
    q=CreativePart.objects.filter(creator=creator)
    main = {'', 'text', 'bild', 'ink', 'orig'}
    episodes = orderEpisodeQuery(Episode.objects.filter
                                 (creativepart__in=q.filter(role__in=main))) \
        .select_related('title') \
        .select_related('orig_name') \
        .prefetch_related('creativepart_set__creator') \
        .prefetch_related('publication_set__issue') \
        .prefetch_related('ref_keys') \
        .all()
    key = RefKey.objects.filter(kind='P', slug=slug).first()
    if key:
        articles = key.article_set.all()
    else:
        articles = None
    wa = Article.objects.filter(creators=creator)
    xe = orderEpisodeQuery(Episode.objects.filter
                           (creativepart__in=q.exclude(role__in=main))).all() \
        .select_related('title')

    covers = creator.issue_set.all()
    allcovers = None
    if len(covers) > 30:
        allcovers = covers
        # The strange arithmetic here is to put 0 (unknown) last rather than first.
        covers = creator.issue_set.order_by((F('cover_best')+99) % 100, 'year')[:20]

    xcred = {t: [ee for ee in xe if ee.title==t] for t in {e.title for e in xe}}
    ROLE = {
        'color': u'färgläggare',
        'redax': u'redaktion',
        'xlat': u'översättare',
        'textning': u'textsättare',
    }
    xroles = ', '.join(ROLE[r] for r in {p.role for p in q if p.role not in main})
    return render_to_response('creator.html', ctx(creator=creator,
                                                  episodes=episodes,
                                                  covers=covers,
                                                  allcovers=allcovers,
                                                  xcred=xcred,
                                                  xroles=xroles,
                                                  articles=articles,
                                                  writtenarticles=wa,
                                                  pagetitle=str(creator)))

def creators(request):
    # The filter should be removed when cover images are better handled.
    creators = Creator.objects.order_by('name') \
      .annotate(first=Min('creativepart__episode__publication__issue__year')) \
      .annotate(latest=Max('creativepart__episode__publication__issue__year')) \
      .annotate(count=Count('creativepart__episode')) \
      .filter(count__gt=0).all()
    return render_to_response('list.html', {
        'pagetitle': 'Serieskapare i Fantomentidningen',
        'items': creators,
    })

def robots(request):
    return HttpResponse('', content_type='text/plain')

def redirectold(request, exception):
    path = request.path_info.lower()
    if path.endswith('index.html'):
        path = path[:-10]
    elif path.endswith('.html'):
        path = path[:-5]
    path = re.sub('^/fa-', '/fa/', path)
    path = re.sub('__+', '_', path).replace('-', '')
    path = settings.FORWARDS.get(path, path)
    if path.startswith('/who/'):
        nameslug = path[5:]
        for n in ALIASES.keys():
            from django.utils.text import slugify
            if nameslug == slugify(n):
                match = name_alias(n)
                path = Creator.objects.get(name=match[0]).get_absolute_url()
    urlconf = getattr(request, 'urlconf', None)
    if (path != request.path_info and
        urlresolvers.is_valid_path(path, urlconf)):
        return HttpResponsePermanentRedirect("%s://%s%s" % (
            'https' if request.is_secure() else 'http',
            request.get_host(), path))
    path = path + '/'
    if (path != request.path_info and
        urlresolvers.is_valid_path(path, urlconf)):
        return HttpResponsePermanentRedirect("%s://%s%s" % (
            'https' if request.is_secure() else 'http',
            request.get_host(), path))
    return page_not_found(request, exception)
