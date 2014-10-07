# -*- encoding: utf-8; -*-
from django.core import urlresolvers
from django.db.models import Count, Min, Max, Avg
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.views.defaults import page_not_found
from libris.models import *
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
    return query.annotate(Min('publication__issue__year')).annotate(Min('publication__issue__number')).order_by('publication__issue__number__min').order_by('publication__issue__year__min')

def allPhantoms():
    # The Avg annotation is a hack to get 1,2,..,9,10 rather than 1,10,11,..,2
    return RefKey.objects.annotate(n=Avg('slug')).order_by('n') \
                 .filter(kind='F').annotate(Count('episode')).all()

def index(request):
    years = Issue.objects.order_by('year').distinct().values_list('year', flat=True)
    titles = Title.objects.order_by('title')
    refs = RefKey.objects.order_by('title').filter(kind='X')
    people = Creator.objects.order_by('name')
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
        'n_issues': Issue.objects.filter(publication__ordno__lt=4711).distinct().count(),
        'years': years,
        'phantoms': allPhantoms(),
        'titles': weighted(titles, 'episode', 4),
        'refs': weighted(refs, 'episode', 3),
        'people': weighted(people, 'creativepart', 10)
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
        ssnum = int('%d%d' % (issue.year, issue.number))
        if (ssnum in SERIESAMOMSLAG):
            issue.omslagurl = 'http://www.seriesam.com/pc/fantomen%d.jpg' % ssnum
        issue.contents = issue.publication_set.all()
        for p in issue.contents:
            if p.episode:
                p.otherpub = [op for op in p.episode.publication_set.all()
                              if op.issue != issue]
    return render_to_response('year.html', ctx(year=int(year), issues=issues,
                                               navyears=getNavYears(year),
                                               pagetitle='Fantomen %s' %(year)))

def title(request, slug, pagesize=200):
    title = get_object_or_404(Title, slug=slug)
    count = title.episode_set.count()
    episodes = orderEpisodeQuery(title.episode_set) \
        .select_related('orig_name') \
        .prefetch_related('creativepart_set__creator') \
        .prefetch_related('publication_set__issue') \
        .prefetch_related('ref_keys') \
        .all()
    key = RefKey.objects.filter(kind='T', slug=slug).first()
    if key:
        articles = key.article_set.all()
    else:
        articles = None
    if count >= 2*pagesize:
        pages = range(1 + count / pagesize)
        page = int(request.GET.get('page', 0))
        episodes = episodes[page*pagesize:(page+1)*pagesize]
    else:
        pages = None

    return render_to_response('title.html', ctx(title=title, episodes=episodes,
                                                articles=articles,
                                                pagetitle=unicode(title),
                                                pages=pages))

def refKey(request, slug):
    refkey = get_object_or_404(RefKey, slug=slug)
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
        pagetitle=unicode(refkey)))

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
    episodes = orderEpisodeQuery(Episode.objects.filter(creativepart__in=q)) \
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
    return render_to_response('creator.html', ctx(creator=creator,
                                                  episodes=episodes,
                                                  articles=articles,
                                                  pagetitle=unicode(creator)))

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

def redirectold(request):
    path = request.path_info.lower()
    if path.endswith('index.html'):
        path = path[:-10]
    elif path.endswith('.html'):
        path = path[:-5]
    if path in ['/who/', '/what/']:
        path = '/'
    path = re.sub('^/fa-', '/fa/', path)
    path = re.sub('__+', '_', path).replace('-', '') \
             .replace('_2_an', '_2an').replace('_o_shay', '_oshay')
    urlconf = getattr(request, 'urlconf', None)
    if (path != request.path_info and
        urlresolvers.is_valid_path(path, urlconf)):
        return HttpResponsePermanentRedirect("%s://%s%s" % (
            'https' if request.is_secure() else 'http',
            request.get_host(), path))
    return page_not_found(request)

SERIESAMOMSLAG = {
    # Based on list I got in mail from Thomas E/seriesam <thom@seriesam.com>
    19501, 19502, 19503, 19504, 19505, 19506, 19507, 19511,
    195110, 195111, 195112, 195113, 195114, 195115, 195116, 195117,
    195118, 195119, 19512, 195120, 195121, 195122, 195123, 195124,
    195125, 195126, 19513, 19514, 19515, 19516, 19517, 19518, 19519,
    19521, 195210, 195211, 195212, 195213, 195214, 195215, 195216,
    195217, 195218, 195219, 19522, 195220, 195221, 195222, 195223,
    195224, 195225, 195226, 19523, 19524, 19525, 19526, 19527, 19528,
    19529, 19531, 195310, 195311, 195312, 195313, 195314, 195315,
    195316, 195317, 195318, 195319, 19532, 195320, 195321, 195322,
    195323, 195324, 195325, 195326, 19533, 19534, 19535, 19536, 19537,
    19538, 19539, 19541, 195410, 195411, 195412, 195413, 195414,
    195415, 195416, 195417, 195418, 195419, 19542, 195420, 195421,
    195422, 195423, 195424, 195425, 195426, 19543, 19544, 19545,
    19546, 19547, 19548, 19549, 19551, 195510, 195511, 195512, 195513,
    195514, 195515, 195516, 195517, 195518, 195519, 19552, 195520,
    195521, 195522, 195523, 195524, 195525, 195526, 19553, 19554,
    19555, 19556, 19557, 19558, 19559, 19561, 195610, 195611, 195612,
    195613, 195614, 195615, 195616, 195617, 195618, 195619, 19562,
    195620, 195621, 195622, 195623, 195624, 195625, 195626, 19563,
    19564, 19565, 19566, 19567, 19568, 19569, 19571, 195710, 195711,
    195712, 195713, 195714, 195715, 195716, 195717, 195718, 195719,
    19572, 195720, 195721, 195722, 195723, 195724, 195725, 195726,
    19573, 19574, 19575, 19576, 19577, 19578, 19579, 19581, 195810,
    195811, 195812, 195813, 195814, 195815, 195816, 195817, 195818,
    195819, 19582, 195820, 195821, 195822, 195823, 195824, 195825,
    195826, 195827, 195828, 195829, 19583, 195830, 195831, 195832,
    195833, 195834, 195835, 195836, 195837, 195838, 19584, 19585,
    19586, 19587, 19588, 19589, 19591, 195910, 195911, 195912, 195913,
    195914, 195915, 195916, 195917, 195918, 195919, 19592, 195920,
    195921, 195922, 195923, 195924, 195925, 195926, 195927, 19593,
    19594, 19595, 19596, 19597, 19598, 19599, 19601, 196010, 196011,
    196012, 196013, 19602, 19603, 19604, 19605, 19606, 19607, 19608,
    19609, 19611, 196110, 196111, 196112, 196113, 19612, 19613, 19614,
    19615, 19616, 19617, 19618, 19619, 19621, 196210, 196211, 196212,
    196213, 19622, 19623, 19624, 19625, 19626, 19627, 19628, 19629,
    19631, 196310, 196311, 196312, 196313, 19632, 19633, 19634, 19635,
    19636, 19637, 19638, 19639, 19641, 196410, 196411, 196412, 196413,
    196414, 196415, 196416, 196417, 196418, 19642, 19643, 19644,
    19645, 19646, 19647, 19648, 19649, 19651, 196510, 196511, 196512,
    196513, 196514, 196515, 196516, 196517, 196518, 196519, 19652,
    19653, 19654, 19655, 19656, 19657, 19658, 19659, 19661, 196610,
    196611, 196612, 196613, 196614, 196615, 196616, 196617, 196618,
    196619, 19662, 196620, 19663, 19664, 19665, 19666, 19667, 19668,
    19669, 19671, 196710, 196711, 196712, 196713, 196714, 196715,
    196716, 196717, 196718, 196719, 19672, 196720, 19673, 19674,
    19675, 19676, 19677, 19678, 19679, 19681, 196810, 196811, 196812,
    196813, 196814, 196815, 196816, 196817, 196818, 196819, 19682,
    196820, 196821, 196822, 196823, 196824, 196825, 196826, 19683,
    19684, 19685, 19686, 19687, 19688, 19689, 19691, 196910, 196911,
    196912, 196913, 196914, 196915, 196916, 196917, 196918, 196919,
    19692, 196920, 196921, 196922, 196923, 196924, 196925, 196926,
    19693, 19694, 19695, 19696, 19697, 19698, 19699, 19701, 197010,
    197011, 197012, 197013, 197014, 197015, 197016, 197017, 197018,
    197019, 19702, 197020, 197021, 197022, 197023, 197024, 197025,
    197026, 19703, 19704, 19705, 19706, 19707, 19708, 19709, 19711,
    197110, 197111, 197112, 197113, 197114, 197115, 197116, 197117,
    197118, 197119, 19712, 197120, 197121, 197122, 197123, 197124,
    197125, 197126, 19713, 19714, 19715, 19716, 19717, 19718, 19719,
    19721, 197210, 197211, 197212, 197213, 197214, 197215, 197216,
    197217, 197218, 197219, 19722, 197220, 197221, 197222, 197223,
    197224, 197225, 197226, 19723, 19724, 19725, 19726, 19727, 19728,
    19729, 19731, 197310, 197311, 197312, 197313, 197314, 197315,
    197316, 197317, 197318, 197319, 19732, 197320, 197321, 197322,
    197323, 197324, 197325, 197326, 19733, 19734, 19735, 19736, 19737,
    19738, 19739, 19741, 197410, 197411, 197412, 197413, 197414,
    197415, 197416, 197417, 197418, 197419, 19742, 197420, 197421,
    197422, 197423, 197424, 197425, 197426, 19743, 19744, 19745,
    19746, 19747, 19748, 19749, 19751, 197510, 197511, 197512, 197513,
    197514, 197515, 197516, 197517, 197518, 197519, 19752, 197520,
    197521, 197522, 197523, 197524, 197525, 197526, 19753, 19754,
    19755, 19756, 19757, 19758, 19759, 19761, 197610, 197611, 197612,
    197613, 197614, 197615, 197616, 197617, 197618, 197619, 19762,
    197620, 197621, 197622, 197623, 197624, 197625, 197626, 197627,
    19763, 19764, 19765, 19766, 19767, 19768, 19769, 19771, 197710,
    197711, 197712, 197713, 197714, 197715, 197716, 197717, 197718,
    197719, 19772, 197720, 197721, 197722, 197723, 197724, 197725,
    197726, 19773, 19774, 19775, 19776, 19777, 19778, 19779, 19781,
    197810, 197811, 197812, 197813, 197814, 197815, 197816, 197817,
    197818, 197819, 19782, 197820, 197821, 197822, 197823, 197824,
    197825, 197826, 19783, 19784, 19785, 19786, 19787, 19788, 19789,
    19791, 197910, 197911, 197912, 197913, 197914, 197915, 197916,
    197917, 197918, 197919, 19792, 197920, 197921, 197922, 197923,
    197924, 197925, 197926, 19793, 19794, 19795, 19796, 19797, 19798,
    19799, 19801, 198010, 198011, 198012, 198013, 198014, 198015,
    198016, 198017, 198018, 198019, 19802, 198020, 198021, 198022,
    198023, 198024, 198025, 198026, 19803, 19804, 19805, 19806, 19807,
    19808, 19809, 19811, 198110, 198111, 198112, 198113, 198114,
    198115, 198116, 198117, 198118, 198119, 19812, 198120, 198121,
    198122, 198123, 198124, 198125, 198126, 19813, 19814, 19815,
    19816, 19817, 19818, 19819, 19821, 198210, 198211, 198212, 198213,
    198214, 198215, 198216, 198217, 198218, 198219, 19822, 198220,
    198221, 198222, 198223, 198224, 198225, 198226, 19823, 19824,
    19825, 19826, 19827, 19828, 19829, 19831, 198310, 198311, 198312,
    198313, 198314, 198315, 198316, 198317, 198318, 198319, 19832,
    198320, 198321, 198322, 198323, 198324, 198325, 198326, 198327,
    19833, 19834, 19835, 19836, 19837, 19838, 19839, 19841, 198410,
    198411, 198412, 198413, 198414, 198415, 198416, 198417, 198418,
    198419, 19842, 198420, 198421, 198422, 198423, 198424, 198425,
    198426, 19843, 19844, 19845, 19846, 19847, 19848, 19849, 19851,
    198510, 198511, 198512, 198513, 198514, 198515, 198516, 198517,
    198518, 198519, 19852, 198520, 198521, 198522, 198523, 198524,
    198525, 198526, 19853, 19854, 19855, 19856, 19857, 19858, 19859,
    19861, 198610, 198611, 198612, 198613, 198614, 198615, 198616,
    198617, 198618, 198619, 19862, 198620, 198621, 198622, 198623,
    198624, 198625, 198626, 19863, 19864, 19865, 19866, 19867, 19868,
    19869, 19871, 198710, 198711, 198712, 198713, 198714, 198715,
    198716, 198717, 198718, 198719, 19872, 198720, 198721, 198722,
    198723, 198724, 198725, 198726, 19873, 19874, 19875, 19876, 19877,
    19878, 19879, 19881, 198810, 198811, 198812, 198813, 198814,
    198815, 198816, 198817, 198818, 198819, 19882, 198820, 198821,
    198822, 198823, 198824, 198825, 198826, 19883, 19884, 19885,
    19886, 19887, 19888, 19889, 19891, 198910, 198911, 198912, 198913,
    198914, 198915, 198916, 198917, 198918, 198919, 19892, 198920,
    198921, 198922, 198923, 198924, 198925, 198926, 19893, 19894,
    19895, 19896, 19897, 19898, 19899, 19901, 199010, 199011, 199012,
    199013, 199014, 199015, 199016, 199017, 199018, 199019, 19902,
    199020, 199021, 199022, 199023, 199024, 199025, 199026, 19903,
    19904, 19905, 19906, 19907, 19908, 19909, 19911, 199110, 199111,
    199112, 199113, 199114, 199115, 199116, 199117, 199118, 199119,
    19912, 199120, 199121, 199122, 199123, 199124, 199125, 199126,
    19913, 19914, 19915, 19916, 19917, 19918, 19919, 19921, 199210,
    199211, 199212, 199213, 199214, 199215, 199216, 199217, 199218,
    199219, 19922, 199220, 199221, 199222, 199223, 199224, 199225,
    199226, 19923, 19924, 19925, 19926, 19927, 19928, 19929, 19931,
    199310, 199311, 199312, 199313, 199314, 199315, 199316, 199317,
    199318, 199319, 19932, 199320, 199321, 199322, 199323, 199324,
    199325, 199326, 19933, 19934, 19935, 19936, 19937, 19938, 19939,
    19941, 199410, 199411, 199412, 199413, 199414, 199415, 199416,
    199417, 199418, 199419, 19942, 199420, 199421, 199422, 199423,
    199424, 199425, 199426, 19943, 19944, 19945, 19946, 19947, 19948,
    19949, 19951, 199510, 199511, 199512, 199513, 199514, 199515,
    199516, 199517, 199518, 199519, 19952, 199520, 199521, 199522,
    199523, 199524, 199525, 199526, 19953, 19954, 19955, 19956, 19957,
    19958, 19959, 19961, 199610, 199611, 199612, 199613, 199614,
    199615, 199616, 199617, 199618, 199619, 19962, 199620, 199621,
    199622, 199623, 199624, 199625, 199626, 19963, 19964, 19965,
    19966, 19967, 19968, 19969, 19971, 199710, 199711, 199712, 199713,
    199714, 199715, 199716, 199717, 199718, 199719, 19972, 199720,
    199721, 199722, 199723, 199724, 199725, 199726, 19973, 19974,
    19975, 19976, 19977, 19978, 19979, 19981, 199810, 199811, 199812,
    199813, 199814, 199815, 199816, 199817, 199818, 199819, 19982,
    199820, 199821, 199822, 199823, 199824, 199825, 199826, 19983,
    19984, 19985, 19986, 19987, 19988, 19989, 19991, 199910, 199911,
    199912, 199913, 199914, 199915, 199916, 199917, 199918, 199919,
    19992, 199920, 199921, 199922, 199923, 199924, 199925, 199926,
    19993, 19994, 19995, 19996, 19997, 19998, 19999, 20001, 200010,
    200011, 200012, 200013, 200014, 200015, 200016, 200017, 200018,
    200019, 20002, 200020, 200021, 200022, 200023, 200024, 200025,
    200026, 20003, 20004, 20005, 20006, 20007, 20008, 20009, 20011,
    200110, 200111, 200112, 200113, 200114, 200115, 200116, 200117,
    200118, 200119, 20012, 200120, 200121, 200122, 200123, 200124,
    200125, 200126, 20013, 20014, 20015, 20016, 20017, 20018, 20019,
    20021, 200210, 200211, 200212, 200213, 200214, 200215, 200216,
    200217, 200218, 200219, 20022, 200220, 200221, 200222, 200223,
    200224, 200225, 200226, 20023, 20024, 20025, 20026, 20027, 20028,
    20029, 20031, 200310, 200311, 200312, 200313, 200314, 200315,
    200316, 200317, 200318, 200319, 20032, 200320, 200321, 200322,
    200323, 200324, 200325, 200326, 20033, 20034, 20035, 20036, 20037,
    20038, 20039, 20041, 200410, 200411, 200412, 200413, 200414,
    200415, 200416, 200417, 200418, 200419, 20042, 200420, 200421,
    200422, 200423, 200425, 200426, 20043, 20044, 20045, 20046, 20047,
    20048, 20049, 20051, 200510, 200511, 200512, 200513, 200514,
    200515, 200516, 200517, 200518, 200519, 20052, 200520, 200521,
    200522, 200523, 200524, 200525, 200526, 20053, 20054, 20055,
    20056, 20057, 20058, 20059, 20061, 200610, 200612, 200615, 200616,
    200617, 200618, 200619, 20062, 200620, 200621, 200622, 200624,
    200625, 200626, 20063, 20064, 20065, 20066, 20067, 20069, 20071,
    200710, 200712, 200713, 200714, 200715, 200716, 200717, 200718,
    200719, 20072, 200720, 200721, 200722, 200724, 200725, 200726,
    20073, 20074, 20075, 20076, 20077, 20078, 20079, 20081, 200810,
    200812, 200813, 200814, 200815, 200816, 200817, 20082, 20083,
    20084, 20085, 20086, 20088, 20089,
}
