# -*- coding: utf-8 -*-
from django.db import models
from fandjango.libris.alias import name_alias
from fandjango.libris.util import makeslug

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

    def __unicode__(self):
        return unicode(self.name)
    
class Issue(models.Model):
    '''A single issue'''
    year = models.PositiveSmallIntegerField()
    number = models.PositiveSmallIntegerField()
    pages = models.PositiveSmallIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2,
                                null=True, blank=True)
    cover_by = models.ManyToManyField(Creator)
    cover_best = models.PositiveSmallIntegerField(
        blank=True, default=0,
        help_text='Position of this cover in yearly competition.')
                                                  
    
    class Meta:
        ordering = ('year', 'number')
        unique_together = ('year', 'number')
    
    def __unicode__(self):
        return u'Fa %s %s' % (self.number, self.year)

class Title(models.Model):
    '''A (reocurring) title'''
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, **kwargs):
        if not self.slug:
            self.slug = makeslug(self.title)
        models.Model.save(self, kwargs)

    def __unicode__(self):
        return u'%s' % (self.title)

class RefKey(models.Model):
    '''Something that exists in the Phantom universe.
    May be a place, a person, a thing or even a concept.'''
    KIND_CHOICES=(
        ('F', 'Fantomen'),
        ('T', 'Serietitel'),
        ('P', 'Real-life person (artist, writer, etc)'),
        ('X', 'In-story object'),
        )
    title = models.CharField(max_length=200, unique=True)
    kind = models.CharField(max_length=1, choices=KIND_CHOICES, default='X')
    slug = models.SlugField(unique=True)

    class Meta:
        unique_together = ('kind', 'slug')
        ordering = ('kind', 'slug')
    
    def save(self, **kwargs):
        if not self.slug:
            self.slug = makeslug(self.title)
        models.Model.save(self, kwargs)

    def get_absolute_url(self):
        '''Get a hyperlink to page for this reference.'''
        return u'/what/%s' % (self.slug)
    
    def __unicode__(self):
        return u'%s' % (self.title)

    @classmethod
    def FA(cls, n):
        n = unicode(n)
        result, new = cls.objects.get_or_create(title='Den %s:e Fantomen' % n,
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
        result, new = cls.objects.get_or_create(title=k)
        return result
    
class DaystripRun(models.Model):
    fromdate = models.DateField()
    todate = models.DateField()
    is_sundays = models.BooleanField(default=False)
    
class Episode(models.Model):
    '''An episode such as it occurs in an Issue.  This might mean an
    episode of a reoccuring title, a part of such an episode, a
    one-shot or a part of a one-shot.'''
    title = models.ForeignKey(Title)
    episode = models.CharField(max_length=200)
    part_no = models.PositiveSmallIntegerField(blank=True, null=True)
    part_name = models.CharField(max_length=200, blank=True)
    teaser = models.TextField(blank=True)
    note = models.TextField(blank=True)
    ref_keys = models.ManyToManyField(RefKey)
    daystrip = models.ForeignKey(DaystripRun, blank=True, null=True)
    firstpub = models.DateField(blank=True, null=True)
    copyright = models.CharField(max_length=200, blank=True)

    _ROLES = (
        ('', 'Av'),
        ('text', 'Text:'),
        ('bild', 'Bild:'),
        ('ink', 'Tush:'),
        ('color', u'Färgläggning:'),
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
    
    def __unicode__(self):
        if self.part_no:
            return u'%s: %s del %s: %s' % (self.title, self.episode,
                                           self.part_no, self.part_name)
        else:
            return u'%s: %s' % (self.title, self.episode)

class CreativePart(models.Model):
    episode = models.ForeignKey(Episode)
    creator = models.ForeignKey(Creator)
    alias = models.CharField(max_length=200, blank=True)
    role = models.CharField(max_length=10, blank=True)
    
    def name(self):
        return self.alias or self.creator.name
    
    def __unicode__(self):
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
    note = models.TextField(blank=True)
    
    def __unicode__(self):
        if self.subtitle:
            return u'%s: %s' % (self.title, self.subtitle)
        else:
            return unicode(self.title)
    
class Publication(models.Model):
    issue = models.ForeignKey(Issue)
    ordno = models.PositiveSmallIntegerField(default=4711)
    label = models.CharField(max_length=200, blank=True)
    
    episode = models.ForeignKey(Episode, null=True)
    best_plac = models.PositiveSmallIntegerField(
        blank=True, default=0,
        help_text='Position of this episode in yearly competition.')
    
    article = models.ForeignKey(Article, null=True)
    
    def get_absolute_url(self):
        '''Get a hyperlink to the issue containing this publication, anchor on year page.'''
        return u'/%d#i%d' % (self.issue.year, self.issue.number)
    
    def __unicode__(self):
        return unicode(self.issue)

    class Meta:
        ordering = ('issue', 'ordno')
        unique_together = ('issue', 'episode', 'article')
