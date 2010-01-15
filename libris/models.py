# -*- coding: utf-8 -*-
from django.db import models

def makeslug(string):
    from re import sub
    t = string.lower()
    for p, r in ((u'[åäáàâã]', 'a'),
                 (u'[éèëêẽ]', 'e'),
                 (u'[íìïîĩ]', 'i'),
                 (u'[úùüûũ]', 'u'),
                 (u'[ńǹñ]', 'n'),
                 (u'[óòöôõ]', 'o'),
                 (r'[^a-z0-9 ]', ''), 
                 (r'\s+', '_')):
        t = sub(p, r, t)
    return t

class Issue(models.Model):
    '''A single issue'''
    year = models.PositiveSmallIntegerField()
    number = models.PositiveSmallIntegerField()
    pages = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("year", "number")
    
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
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, **kwargs):
        if not self.slug:
            self.slug = makeslug(self.title)
        models.Model.save(self, kwargs)

    def __unicode__(self):
        return u'%s' % (self.title)
    
class Episode(models.Model):
    '''An episode such as it occurs in an Issue.  This might mean an
    episode of a reoccuring title, a part of such an episode, a
    one-shot or a part of a one-shot.'''
    title = models.ForeignKey(Title)
    episode = models.CharField(max_length=200)
    part_no = models.PositiveSmallIntegerField(blank=True, null=True)
    part_name = models.CharField(max_length=200, blank=True)
    teaser = models.TextField(blank=True)
    ref_keys = models.ManyToManyField(RefKey)

    def __unicode__(self):
        if self.part_no:
            return u'%s: %s del %s: %s' % (self.title, self.episode,
                                           self.part_no, self.part_name)
        else:
            return u'%s: %s' % (self.title, self.episode)
        
class Publication(models.Model):
    issue = models.ForeignKey(Issue)
    episode = models.ForeignKey(Episode)
    ordno = models.PositiveSmallIntegerField()
