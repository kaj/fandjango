from django.conf import settings
from django.core.management.base import BaseCommand
from libris.models import *
from xml.dom.minidom import parse
from minixpath import *
from os import path
from optparse import make_option

class Command(BaseCommand):
    help = 'Find and read data files'

    option_list = BaseCommand.option_list + (
        make_option('--dir', help='Directory to read data from',
                    dest='dir'),
        )

    def handle(self, *args, **options):
        dir = options.get('dir') or '../fantomen'
        years = args or range(1950, 2015)
        for year in years:
            file = path.join(dir, '%s.data' % year)
            if path.exists(file):
                print "Should read from", file
                read_data_file(file)
            else:
                print "No such file: %s" % file
        # Clean up stray data
        Article.objects.filter(publication=None).delete()
        Episode.objects.filter(publication=None).delete()
        kh = RefKey.FA('22')
        k = RefKey.FA('22.1')
        h = RefKey.FA('22.2')
        for e in kh.episode_set.all():
            e.ref_keys = set.union({k, h}, e.ref_keys.all())
        kh.delete()

def getBestPlac(elem):
    bestElem = evaluate(elem, '/best')
    if bestElem:
        return int(bestElem[0].getAttribute('plac'))
    else:
        return 0

def read_data_file(filename):
    dom = parse(filename)
    year = getText(evaluate(dom, "/libris/info/year")[0]);
    for issueElement in evaluate(dom, "/libris/issue"):
        coverElem = evaluate(issueElement, '/omslag')
        pages = issueElement.getAttribute('pages') or None
        price =  issueElement.getAttribute('price') or None
        cover_best = getBestPlac(coverElem[0]) if coverElem else 0
        nrattr = issueElement.getAttribute("nr")
        issue, issue_is_new = Issue.objects.get_or_create(
            year=year,
            number=issueNr(nrattr),
            defaults={'pages': pages, 'price': price, 'numberStr': nrattr,
                      'cover_best': cover_best})
        if not issue_is_new:
            issue.pages = pages
            issue.price =  price
            issue.cover_best = cover_best
            issue.numberStr=nrattr
            issue.save()
        # Purge before creating new content
        issue.publication_set.all().delete()
        ordno = 0;
        print "Found issue:", issue
        for item in issueElement.childNodes:
            ordno = ordno + 1
            if item.nodeType != 1:
                continue
            if item.tagName == 'omslag':
                cbe = evaluate(item, '/by')
                if cbe:
                    issue.cover_by = [Creator.objects.get_or_create(name=name)[0]
                                      for name, alias
                                      in [name_alias(who) for who
                                          in getByWho(*cbe)]]
                
            elif item.tagName == 'serie':
                title, title_is_new = Title.objects.get_or_create(
                    title=getText(evaluate(item, "/title")[0]))
                if title_is_new:
                    print "FOUND NEW TITLE:", title
                episodename = getText(*evaluate(item, "/episode")[:1]) or ''
                part_no, part_name = None, ''
                partElem = evaluate(item, "/part")
                if partElem:
                    no = partElem[0].getAttribute("no");
                    if no:
                        part_no = no
                    part_name = getText(partElem[0]);
                if episodename or part_no or part_name:
                    episode, is_new_episode = Episode.objects.get_or_create(
                        title=title, episode=episodename,
                        part_no=part_no, part_name=part_name)
                else:
                    episode = Episode(title=title, episode=episodename,
                                      part_no=part_no, part_name=part_name)
                    episode.save() # get an id
                    is_new_episode = True
                episode.teaser = getText(*evaluate(item, "/teaser")) or \
                                 episode.teaser
                episode.note = getText(*evaluate(item, "/note")) or \
                               episode.note
                episode.copyright = getText(*evaluate(item, '/copyright')) or \
                                    episode.copyright
                
                origNameElem = evaluate(item, '/episode[@role ="orig"]')
                if origNameElem and not episode.orig_name:
                    print "FOUND ORIGNAME", origNameElem
                    episode.orig_name, eon_isnew = \
                        ForeignName.objects.get_or_create(
                        title=getText(origNameElem[0]),
                        language=origNameElem[0].getAttribute("xml:lang"))
                elif origNameElem:
                    print "FOUND ORIGNAME", origNameElem, "ignoring it."
                    
                stripElem = evaluate(item, '/daystrip')
                if stripElem:
                    fromdate = evaluate(stripElem[0], '/from')
                    todate = evaluate(stripElem[0], '/to')
                    if fromdate and todate:
                        episode.daystrip = DaystripRun.objects.create(
                            fromdate=getText(*fromdate),
                            todate=getText(*todate),
                            is_sundays=(stripElem[0].getAttribute('d') == 'sun'))
                    else:
                        print "Unknown kind of daystrip: %s" % stripElem
                
                episode.ref_keys = set.union(getRefKeys(item),
                                             episode.ref_keys.all())
                
                for byElem in evaluate(item, "/by"):
                    role = byElem.getAttribute('role')
                    for who in getByWho(byElem):
                        CreativePart_create(episode, who, role)

                origPubElem = evaluate(item, "/prevpub/date")
                if origPubElem:
                    episode.firstpub = getText(*origPubElem)
                
                prevPubElem = evaluate(item, '/prevpub[magazine!=""]')
                if prevPubElem:
                    if not episode.prevpub.count():
                        episode.prevpub = [
                            prevpub for prevpub, isnew in
                            [OtherMag.objects.get_or_create(
                                    title=getText(*evaluate(ppe, "/magazine")),
                                    issue=getText(*evaluate(ppe, "/issue")) or None,
                                    i_of=getText(*evaluate(ppe, "/of")) or None,
                                    year=getText(*evaluate(ppe, "/year")) or None)
                             for ppe in prevPubElem]]
                episode.save();
                Publication(issue=issue, episode=episode, ordno=ordno,
                            label=getText(*evaluate(item, "/label")) or '',
                            best_plac=getBestPlac(item)).save()
                prevFaElem = evaluate(item, "/prevpub[fa!='']")
                for e in prevFaElem:
                    fa = issueNr(getText(evaluate(e, "/fa")[0]))
                    y = getText(evaluate(e, "/year")[0])
                    i = Issue.objects.get_or_create(year=y, 
                                                    number=fa)[0]
                    Publication.objects.get_or_create(episode=episode, issue=i)
                
                #print "Serie", episode
            elif item.tagName == 'text':
                article = Article.objects.create(
                    title=getText(*evaluate(item, '/title')),
                    subtitle=getText(*evaluate(item, '/subtitle')),
                    note = getText(*evaluate(item, "/note")))
                keys = getRefKeys(item)
                if keys:
                    article.ref_keys = keys
                creators = evaluate(item, "/by")
                if creators:
                    article.creators = [Creator.objects.get_or_create(name=name)[0]
                                        for name, alias
                                        in [name_alias(who) for who
                                            in getByWho(*creators)]]
                if keys or creators:
                    article.save()
                Publication(issue=issue, article=article, ordno=ordno).save()
                
            else:
                print 'Element', item.tagName
    dom.unlink()

def issueNr(nrstr):
    '''Dubbelnummer 2-3 och prevpub i delar 2/3/4 representeras av 2.'''
    return int(nrstr.split('-',1)[0].split('/',1)[0].split(', ',1)[0])

def getByWho(byElem):
    whoElem = evaluate(byElem, "/who")
    if whoElem:
        return [getText(who) for who in whoElem]
    else:
        return [getText(byElem)]

def getRefKeys(item):
    ref = evaluate(item, "/ref")
    if ref:
        keys = set.union(set(RefKey.FA(k.getAttribute('no'))
                             for k in evaluate(ref[0], '/fa')),
                         set(RefKey.TITLE(getText(s))
                             for s in evaluate(ref[0], '/serie')),
                         set(RefKey.WHO(getText(k))
                             for k in evaluate(ref[0], '/who')),
                         set(RefKey.KEY(getText(k))
                             for k in evaluate(ref[0], '/key')))
        #print "  keys:", keys
        return keys
    else:
        return set()

