# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db.models import Q
from libris.models import *
from optparse import make_option
from os import path
from subprocess import Popen, PIPE
from time import sleep
from xml.dom import minidom as dom
import codecs
import sys

class Command(BaseCommand):
    help = 'Dump data to my traditional xml files'

    option_list = BaseCommand.option_list + (
        make_option('--dir', help='Directory to write data to',
                    dest='dir'),
        )

    def handle(self, *args, **options):
        dir = options.get('dir') or 'dump'
        years = args or Issue.objects.order_by('year').distinct().\
                values_list('year', flat=True)
        for year in years:
            file = path.join(dir, '%s.data' % year)
            print "Should write to", file
            xmlForYear(year).writexml(
                codecs.getwriter('utf-8')(open(file, 'w')),
                encoding='utf-8',
                indent='', addindent='  ', newl='\n')

def addRefKeys(doc, baseElem, keys):
    elem = doc.createElement
    text = doc.createTextNode
    if keys.count():
        ref = baseElem.appendChild(elem('ref'))
        for r in keys.all():
            if r.kind == 'F':
                ref.appendChild(elem('fa')).setAttribute('no', r.slug)
            elif r.kind == 'T':
                ref.appendChild(elem('serie')).appendChild(text(r.title))
            elif r.kind == 'P':
                ref.appendChild(elem('who')).appendChild(text(r.title))
            elif r.kind == 'X':
                ref.appendChild(elem('key')).appendChild(text(r.title))

def xmlEpisode(doc, pub):
    episode, issue = pub.episode, pub.issue
    elem = doc.createElement
    text = doc.createTextNode
    i = elem('serie')
    if pub.label:
        i.appendChild(elem('label')).appendChild(text(pub.label))
    i.appendChild(elem('title')).appendChild(text(episode.title.title))
    if episode.episode:
        i.appendChild(elem('episode')).appendChild(text(episode.episode))
    if episode.orig_name:
        oee = i.appendChild(elem('episode'))
        oee.setAttribute('role', 'orig')
        oee.setAttribute('xml:lang', unicode(episode.orig_name.language))
        oee.appendChild(text(episode.orig_name.title))
    if episode.part_no or episode.part_name:
        px = i.appendChild(elem('part'))
        if episode.part_no:
            px.setAttribute('no', unicode(episode.part_no))
        if episode.part_name:
            px.appendChild(text(episode.part_name))
    if episode.teaser:
        i.appendChild(elem('teaser')).appendChild(text(episode.teaser))
    
    addRefKeys(doc, i, episode.ref_keys)
    
    if episode.note:
        i.appendChild(elem('note')).appendChild(text(episode.note))

    creativeparts = episode.creativepart_set.all()
    for role in Episode.ROLES:
        by = [unicode(p.alias or p.creator)
              for p in creativeparts.filter(role=role)]
        if by:
            px = i.appendChild(byWho(doc, by))
            if role:
                px.setAttribute('role', role)
    
    if episode.daystrip:
        dx = i.appendChild(elem('daystrip'))
        strip=episode.daystrip
        if strip.is_sundays:
            dx.setAttribute('d', 'sun')
        dx.appendChild(elem('from')).appendChild(text(unicode(strip.fromdate)))
        dx.appendChild(elem('to')).appendChild(text(unicode(strip.todate)))

    if episode.firstpub:
        px = i.appendChild(elem('prevpub'))
        px.setAttribute('role', 'orig')
        px.appendChild(elem('date')).appendChild(text(unicode(episode.firstpub)))
        
    for ppub in episode.publication_set.filter(
        Q(issue__year__lt=issue.year)
        or (Q(issue__year=issue.year) and Q(issue__number__lt=issue.number))):
        px = i.appendChild(elem('prevpub'))
        px.appendChild(elem('fa')).appendChild(text(unicode(ppub.issue.number)))
        px.appendChild(elem('year')).appendChild(text(unicode(ppub.issue.year)))
    
    for pp in episode.prevpub.all():
        px = i.appendChild(elem('prevpub'))
        px.appendChild(elem('magazine')).appendChild(text(pp.title))
        if pp.issue:
            px.appendChild(elem('issue')).appendChild(text(unicode(pp.issue)))
        if pp.i_of:
            px.appendChild(elem('of')).appendChild(text(unicode(pp.i_of)))
        if pp.year:
            px.appendChild(elem('year')).appendChild(text(unicode(pp.year)))
            
    if episode.copyright:
        i.appendChild(elem('copyright')).appendChild(text(episode.copyright))

    if pub.best_plac:
        best = i.appendChild(doc.createElement('best'))
        best.setAttribute('plac', unicode(pub.best_plac))

    return i

def xmlArticle(doc, article):
    elem = doc.createElement
    text = doc.createTextNode
    i = elem('text')
    i.appendChild(elem('title')).appendChild(text(article.title))
    if article.subtitle:
        i.appendChild(elem('subtitle')).appendChild(text(article.subtitle))
    addRefKeys(doc, i, article.ref_keys)
    if article.note:
        i.appendChild(elem('note')).appendChild(text(article.note))
    return i

def byWho(doc, by):
    elem = doc.createElement
    text = doc.createTextNode
    result = doc.createElement('by') 
    if len(by) == 1:
        result.appendChild(text(unicode(by[0])))
    else:
        by = list(by)
        for b in by[:-2]:
            result.appendChild(elem('who')).appendChild(text(unicode(b)))
            result.appendChild(text(', '))
        result.appendChild(elem('who')).appendChild(text(unicode(by[-2])))
        result.appendChild(text(' & '))
        result.appendChild(elem('who')).appendChild(text(unicode(by[-1])))
    return result

def xmlForYear(year):
    d=dom.Document()
    libris = d.appendChild(d.createElement('libris'))
    info = libris.appendChild(d.createElement('info'))
    info.appendChild(d.createElement('title')).appendChild(d.createTextNode('Fantomen'))
    info.appendChild(d.createElement('year')).appendChild(d.createTextNode(unicode(year)))
    info.appendChild(d.createElement('note')) \
        .appendChild(d.createTextNode(u'Källa: Respektive tidning.'))
    for issue in Issue.objects.filter(year=year):
        xmli = libris.appendChild(d.createElement('issue'))
        xmli.setAttribute('nr', str(issue.number))
        if issue.pages:
            xmli.setAttribute('pages', str(issue.pages))
        if issue.price:
            xmli.setAttribute('price', str(issue.price))
        cover = d.createElement('omslag')
        cover_by = issue.cover_by.all()
        if len(cover_by) > 0:
            cover.appendChild(byWho(d, cover_by))
        if issue.cover_best:
            best = cover.appendChild(d.createElement('best'))
            best.setAttribute('plac', unicode(issue.cover_best))
        xmli.appendChild(cover)
        for pub in Publication.objects.filter(issue=issue):
            if pub.episode: xmli.appendChild(xmlEpisode(d, pub))
            if pub.article: xmli.appendChild(xmlArticle(d, pub.article))
    return d
