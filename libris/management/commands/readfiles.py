from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from libris.models import *
import xml.etree.ElementTree as ET
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
        years = args or range(1950, datetime.now().year+1)
        for year in years:
            file = path.join(dir, '%s.data' % year)
            if path.exists(file):
                print("Should read from %s" % file)
                read_data_file(file)
            else:
                print("No such file: %s" % file)
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
    bestElem = elem.find('best')
    if bestElem != None:
        return int(bestElem.get('plac'))
    else:
        return 0

def read_data_file(filename):
    et = ET.parse(filename)
    year = et.find('info/year').text;
    for issueElement in et.findall('issue'):
        pages = issueElement.get('pages')
        price =  issueElement.get('price')
        nrattr = issueElement.get('nr')
        coverElem = issueElement.find('omslag')
        cover_best = getBestPlac(coverElem) if coverElem != None else 0
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
        print("Found issue:", issue)
        for item in issueElement.findall('*'):
            ordno = ordno + 1
            if item.tag == 'omslag':
                cbe = item.find('by')
                if cbe != None:
                    issue.cover_by = [Creator.objects.get_or_create(name=name)[0]
                                      for name, alias
                                      in [name_alias(who) for who
                                          in getByWho(cbe)]]
                
            elif item.tag == 'serie':
                title, title_is_new = Title.objects.get_or_create(
                    title=text(item.find('title')))
                if title_is_new:
                    print("FOUND NEW TITLE:", title)
                episodename = text(item.find('episode')) or ''
                part_no, part_name = None, ''
                partElem = item.find('part')
                if partElem != None:
                    no = partElem.get('no')
                    if no:
                        part_no = no
                    part_name = text(partElem)
                episode, is_new_episode = Episode.objects.get_or_create(
                    title=title, episode=episodename)
                episode.teaser = text(item.find('teaser')) or episode.teaser
                episode.note = text(item.find('note')) or episode.note
                episode.copyright = text(item.find('copyright')) or \
                                    episode.copyright
                
                origNameElem = item.find('episode[@role="orig"]')
                if origNameElem != None and not episode.orig_name:
                    print("FOUND ORIGNAME", text(origNameElem),
                          origNameElem.attrib)
                    episode.orig_name, eon_isnew = \
                        ForeignName.objects.get_or_create(
                        title=origNameElem.text,
                        language=origNameElem.get("{http://www.w3.org/XML/1998/namespace}lang"))
                elif origNameElem != None:
                    print("FOUND ORIGNAME", origNameElem, "ignoring it.")
                    
                stripElem = item.find('daystrip')
                if stripElem != None:
                    fromdate = stripElem.find('from')
                    todate = stripElem.find('to')
                    if fromdate != None and todate != None:
                        episode.daystrip = DaystripRun.objects.create(
                            fromdate=fromdate.text,
                            todate=todate.text,
                            is_sundays=(stripElem.get('d') == 'sun'))
                    else:
                        print("Unknown kind of daystrip: %s" % stripElem)
                
                episode.ref_keys = set.union(getRefKeys(item),
                                             episode.ref_keys.all())
                
                for byElem in item.findall('by'):
                    role = byElem.get('role') or ''
                    for who in getByWho(byElem):
                        CreativePart_create(episode, who, role)

                origPubElem = item.find('prevpub/date')
                if origPubElem != None:
                    episode.firstpub = text(origPubElem)
                
                prevPubElem = item.findall('prevpub[magazine!=""]')
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
                            label=text(item.find('label')) or '',
                            part_no=part_no, part_name=part_name,
                            best_plac=getBestPlac(item)).save()
                prevFaElem = item.findall("prevpub[fa!='']")
                for e in prevFaElem:
                    fa, fastr = issueNrStr(getText(evaluate(e, "/fa")[0]))
                    y = getText(evaluate(e, "/year")[0])
                    i = Issue.objects.get_or_create(year=y, number=fa,
                                                    numberStr=fastr)[0]
                    Publication.objects.get_or_create(episode=episode, issue=i)
                
                #print("Serie", episode)
            elif item.tag == 'text':
                article = Article.objects.create(
                    title=text(item.find('title')),
                    subtitle=text(item.find('subtitle')) or '',
                    note = text(item.find('note')) or '')
                keys = getRefKeys(item)
                if keys:
                    article.ref_keys = keys
                creators = item.findall('by')
                if creators:
                    from itertools import chain
                    article.creators = [Creator.objects.get_or_create(name=name)[0]
                                        for name, alias
                                        in [name_alias(who) for who
                                            in chain.from_iterable(
                                                getByWho(creator)
                                                for creator in creators)]]
                if keys or creators:
                    article.save()
                Publication(issue=issue, article=article, ordno=ordno).save()
                
            else:
                print('Element', item.tag)

def issueNrStr(nrstr):
    t = nrstr.split('/', 1)[0].split(', ', 1)[0]
    return (int(t.split('-', 1)[0]), t)

def issueNr(nrstr):
    '''Dubbelnummer 2-3 och prevpub i delar 2/3/4 representeras av 2.'''
    return int(nrstr.split('-',1)[0].split('/',1)[0].split(', ',1)[0])

def getByWho(byElem):
    if byElem == None:
        return []
    whoElem = byElem.findall('who')
    if whoElem:
        return [text(who) for who in whoElem]
    else:
        return [text(byElem)]

def getRefKeys(item):
    ref = item.find('ref')
    if ref != None:
        keys = set.union(
            set(RefKey.FA(k.get('no')) for k in ref.findall('fa')),
            set(RefKey.TITLE(text(s)) for s in ref.findall('serie')),
            set(RefKey.WHO(text(k)) for k in ref.findall('who')),
            set(RefKey.KEY(text(k)) for k in ref.findall('key')))
        #print("  keys:", keys)
        return keys
    else:
        return set()

def text(elem):
    if elem != None:
        return ''.join(elem.itertext())
    else:
        return None

