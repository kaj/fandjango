# -*- coding: utf-8 -*-
from autoslug.fields import AutoSlugField
from django.db import models
from django.template.defaultfilters import date as filterdate
from django.conf import settings
from libris.alias import name_alias
from libris.util import makeslug

class Creator(models.Model):
    '''A person who takes part in creating the comics and/or texts.'''
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, **kwargs):
        if not self.slug:
            self.slug = makeslug(self.name)
        models.Model.save(self, kwargs)

    def get_absolute_url(self):
        '''Get a hyperlink to page for this creator.'''
        return u'/who/%s' % (self.slug)

    def __str__(self):
        return str(self.name)
    
class Issue(models.Model):
    '''A single issue'''
    year = models.PositiveSmallIntegerField()
    number = models.PositiveSmallIntegerField()
    numberStr = models.CharField(
        max_length=5,
        help_text='number in char form, or e.g. "19-20" for double.')
    pages = models.PositiveSmallIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2,
                                null=True, blank=True)
    cover_by = models.ManyToManyField(Creator, blank=True)
    cover_best = models.PositiveSmallIntegerField(
        blank=True, default=0,
        help_text='Position of this cover in yearly competition.')
    ordering = models.PositiveIntegerField()

    class Meta:
        ordering = ('ordering',)
        unique_together = ('year', 'number')
    
    def save(self, **kwargs):
        if not self.ordering:
            self.ordering = int(self.year) * 100 + int(self.number)
        models.Model.save(self, kwargs)

    def coverurl(self):
        return "%sc%s/s%s.jpg" % (settings.STATIC_URL, self.year,
                                  self.numberStr)

    def __str__(self):
        return u'Fa %s %s' % (self.numberStr, self.year)

class Title(models.Model):
    '''A (reocurring) title'''
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, **kwargs):
        if not self.slug:
            self.slug = makeslug(self.title)
        models.Model.save(self, kwargs)

    def __str__(self):
        return u'%s' % (self.title)

    class Meta:
        ordering = ('title',)

class RefKey(models.Model):
    '''Something that exists in the Phantom universe.
    May be a place, a person, a thing or even a concept.'''
    KIND_CHOICES=(
        ('F', 'Fantomen'),
        ('T', 'Serietitel'),
        ('P', 'Real-life person (artist, writer, etc)'),
        ('X', 'In-story object'),
        )
    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=1, choices=KIND_CHOICES, default='X')
    slug = models.SlugField()

    class Meta:
        unique_together = [('kind', 'slug'), ('kind', 'title')]
        ordering = ('kind', 'title')
    
    def save(self, **kwargs):
        if not self.slug:
            self.slug = makeslug(self.title)
        models.Model.save(self, kwargs)

    def get_absolute_url(self):
        '''Get a hyperlink to page for this reference.'''
        if self.kind=='F':
            return u'/fa/%s' % (self.slug)
        elif self.kind=='P':
            return u'/who/%s' % (self.slug)
        elif self.kind=='T':
            return u'/%s' % (self.slug)
        else:
            return u'/what/%s' % (self.slug)
    
    def __str__(self):
        return u'%s' % (self.title)

    def shortFa(self):
        if self.kind=='F' and \
           self.slug not in ['0', '17.1', '22.1','22.2', '22']:
            return self.slug
        else:
            return self.__str__()

    @classmethod
    def FA(cls, n):
        n = str(n)
        special = {'0': 'Kapten Walker',
                   '17.1': 'Julie',
                   '22': 'Kit & Heloise',
                   '22.1': 'Kit',
                   '22.2': 'Heloise',
               }
        result, new = cls.objects.get_or_create(
            title=special.get(n) or ('Den %s:e Fantomen' % n),
            kind='F',
            slug=n)
        return result
    
    @classmethod
    def TITLE(cls, s):
        result, new = cls.objects.get_or_create(title=s, kind='T')
        return result
    
    @classmethod
    def WHO(cls, s):
        result, new = cls.objects.get_or_create(title=s, kind='P')
        return result
    
    @classmethod
    def KEY(cls, k):
        if k == u'Julie':
            return cls.FA('17.1')
        elif k == u'Kit & Heloise':
            # To be replaced with both 21.1 and 21.2 somehow
            return cls.FA('22')
        elif k == u'Kit':
            return cls.FA('22.1')
        elif k == u'Heloise':
            return cls.FA('22.2')
        result, new = cls.objects.get_or_create(title=k, kind='X')
        return result
    
class DaystripRun(models.Model):
    fromdate = models.DateField()
    todate = models.DateField()
    is_sundays = models.BooleanField(default=False)
    
    def __str__(self):
        if self.fromdate != self.todate:
            return u'%s %s - %s.' % (
                u'Söndagssidor' if self.is_sundays else 'Dagstrip',
                filterdate(self.fromdate, 'j F Y'),
                filterdate(self.todate, 'j F Y'))
        else:
            return u'%s %s.' % (
                u'Söndagssida' if self.is_sundays else 'Dagstrip',
                filterdate(self.fromdate, 'j F Y'))

class ForeignName(models.Model):
    """A title (probably the original title) in another language."""
    title = models.CharField(max_length=200)
    language = models.CharField(max_length=5)

class OtherMag(models.Model):
    '''Another magazine etc where a previous publication occurs.'''
    title = models.CharField(max_length=200)
    issue = models.PositiveSmallIntegerField(blank=True, null=True)
    i_of = models.PositiveSmallIntegerField(blank=True, null=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return u''.join([self.title or '',
                         self.issue and ' %d' % self.issue or '',
                         self.i_of and ' of %d' % self.i_of or '',
                         self.year and ' %d' %self.year or ''])
    
class Episode(models.Model):
    '''An episode such as it occurs in an Issue.  This might mean an
    episode of a reoccuring title, a part of such an episode, a
    one-shot or a part of a one-shot.'''
    title = models.ForeignKey(Title)
    episode = models.CharField(max_length=200)
    orig_name = models.ForeignKey(ForeignName, blank=True, null=True)
    teaser = models.TextField(blank=True)
    note = models.TextField(blank=True)
    ref_keys = models.ManyToManyField(RefKey, blank=True)
    daystrip = models.ForeignKey(DaystripRun, blank=True, null=True)
    firstpub = models.DateField(blank=True, null=True)
    prevpub = models.ManyToManyField(OtherMag, blank=True)
    copyright = models.CharField(max_length=200, blank=True)

    _ROLES = (
        ('', 'Av'),
        ('text', 'Text:'),
        ('bild', 'Bild:'),
        ('ink', 'Tush:'),
        ('color', u'Färgläggning:'),
        ('orig', u'Efter en originalberättelse av:'),
        ('redax', u'Redaktion:'),
        ('xlat', u'Översättning:'),
        ('textning', u'Textsättning:'),
        )
    ROLE = dict(_ROLES)
    ROLES = [key for key, name in _ROLES]
    
    def by(self):
        '''Get the creators in [(role, [(slug, name), ...]), ...] format.'''
        result = {}
        for r, c in [(p.role, (p.creator.slug, p.alias or p.creator.name))
                     for p in self.creativepart_set.all()]:
            result[r] = result.get(r, []) + [c]
        
        return [(self.ROLE[r], result[r]) for r in self.ROLES if r in result]
    
    def __str__(self):
        if self.episode:
            return u'%s: %s' % (self.title, self.episode)
        else:
            return u'%s' % self.title

class CreativePart(models.Model):
    episode = models.ForeignKey(Episode)
    creator = models.ForeignKey(Creator)
    alias = models.CharField(max_length=200, blank=True)
    role = models.CharField(max_length=10, blank=True)
    
    def name(self):
        return self.alias or self.creator.name
    
    def __str__(self):
        return self.name()
    
    def _get_slug(self):
        return self.creator.slug
    
    slug = property(_get_slug)

    class Meta:
        unique_together = ('episode', 'creator', 'role')

def CreativePart_create(episode, name, role):
    realname, alias = name_alias(name)
    c, cisnew = Creator.objects.get_or_create(name=realname)
    p, pisnew = CreativePart.objects.get_or_create(episode=episode,
                                                   creator=c,
                                                   role=role,
                                                   defaults={'alias': alias})
    return p

class Article(models.Model):
    '''Something published that is not an episode of a comic.'''
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=500)
    ref_keys = models.ManyToManyField(RefKey)
    creators = models.ManyToManyField(Creator)
    note = models.TextField(blank=True)
    
    def __str__(self):
        if self.subtitle:
            return '%s: %s' % (self.title, self.subtitle)
        else:
            return str(self.title)

    
class Publication(models.Model):
    issue = models.ForeignKey(Issue)
    ordno = models.PositiveSmallIntegerField(default=4711)
    label = models.CharField(max_length=200, blank=True)

    episode = models.ForeignKey(Episode, null=True, blank=True)
    best_plac = models.PositiveSmallIntegerField(
        blank=True, default=0,
        help_text='Position of this episode in yearly competition.')
    part_no = models.PositiveSmallIntegerField(blank=True, null=True)
    part_name = models.CharField(max_length=200, blank=True)
    
    article = models.ForeignKey(Article, null=True, blank=True)
    
    def get_absolute_url(self):
        '''Get a hyperlink to the issue containing this publication, anchor on year page.'''
        return u'/%d#i%d' % (self.issue.year, self.issue.number)

    def is_prev_only(self):
        return self.ordno == 4711
    
    def begins(self):
        return self.part_no is None or self.part_no == 1

    def __str__(self):
        return u'%s' % self.issue

    def __repr__(self):
        return repr(u'%s: %d: %s' % (self.issue, self.ordno,
                                     self.episode or self.article))

    class Meta:
        ordering = ('issue__ordering', 'ordno')
        unique_together = ('issue', 'episode', 'article')
