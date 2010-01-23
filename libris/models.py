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
                 (r'[\s-]+', '_')):
        t = sub(p, r, t)
    return t

class Issue(models.Model):
    '''A single issue'''
    year = models.PositiveSmallIntegerField()
    number = models.PositiveSmallIntegerField()
    pages = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ('year', 'number')
        unique_together = ('year', 'number')
    
    def __unicode__(self):
        return u'Fa %s %s' % (self.number, self.year)

class Creator(models.Model):
    '''A person who takes part in creating the comics and/or texts.'''
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, **kwargs):
        if not self.slug:
            self.slug = makeslug(self.name)
        models.Model.save(self, kwargs)

    def __unicode__(self):
        return u'%s' % (self.name)
    
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

def aliases(name, *alias):
    return [(a,name) for a in alias]

ALIASES = dict(
    aliases(u'Alan Gordon', u'Al Gordon', u'Gordon') +
    aliases(u'Alf Woxnerud', u'Wox') +
    aliases(u'Alfredo Castelli', u'Castelli') +
    aliases(u'Anders Eklund', u'A. Eklund') +
    aliases(u'André Franquin', u'Franquin') +  
    aliases(u'Anette Salmelin', u'A. Salmelin') +  
    aliases(u'Ann Schwenke', u'A. Schwenke') +
    aliases(u'Anniqa Tjernlund', u'A. Tjernlund') +  
    aliases(u'Arthur Conan Doyle', u'A. Conan Doyle') +
    aliases(u'Bengt Sahlberg', u'B. Sahlberg') +
    aliases(u'Bertil Wilhelmsson', u'B. Wilhelmsson', u'Wilhelmsson') +
    aliases(u'Birgit Lundborg', u'Biggan Lundborg', u'B. Lundborg') +
    aliases(u'Björn Ihrstedt', u'B. Ihrstedt', u'B Ihrstedt') +
    aliases(u'Carlos Cruz', u'Carloz Cruz', u'C. Cruz', u'Cruz') +
    aliases(u'Claes Reimerthi', u'C. Reimerthi', u'Reimerthi') +
    aliases(u'César Spadari', u'Cèsar Spadari', u'Cesàr Spadari', u'Cesár Spadari', u'Cesar Spadari', u'C. Spadari', u'Spadari') +  
    aliases(u'Dag R. Frognes', u'Dag Frognes') +
    aliases(u'Dai Darell', u'Darell') +
    aliases(u'Donne Avenell', u'Don Avenell', u'D. Avenell', u'Avenell') +
    aliases(u'Eirik Ildahl', u'Eiric Ildahl') +
    aliases(u'Eugenio Mattozzi', u'E. Mattozzi') +
    aliases(u'Ferdinando Tacconi', u'Fernanino Tacconi', u'Tacconi') +
    aliases(u'Fred Fredericks', u'Fredericks') +
    aliases(u'G. Rosinski', u'Rosinski') +  
    aliases(u'Georges Bessis', u'Georges Bess', u'G. Bess') +
    aliases(u'Germano Ferri', u'Ferri') +
    aliases(u'Hans Jonsson', u'Hans Jonson', u'Hasse Jonsson', u'H. Jonsson', u'H Jonsson') +
    aliases(u'Hans Lindahl', u'Hasse Lindahl', u'H. Lindahl', u'Lindahl') +
    aliases(u'Heiner Bade', u'Helmer Bade', u'H. Bade', u'H Bade', u'H. Baade', u'Bade') + 
    aliases(u'Henrik Brandendorff', u'H. Brandendorff', u'Henrik Nilsson') +
    aliases(u'Idi Kharelli', u'Kharelli') +
    aliases(u'Iréne Gasc', u'Irene Gasc') +
    aliases(u'Iván Boix', u'Ivàn Boix', u'Ivan Boix') +
    aliases(u'J. Van Hamme', u'J Van Hamme', u'Van Hamme') +
    aliases(u'Jaime Vallvé', u'J. Vallvé', u'Vallvé') +
    aliases(u'Janne Lundström', u'Jan Lundström', u'J. Lundström', u'Lundström') +
    aliases(u'Jean Giraud', u'J. Giraud', u'Giraud') +  
    aliases(u'Jean-Michel Charlier', u'J-M. Charlier', u'J-M Charlier', u'Charlier') +
    aliases(u'Jean-Yves Mitton', u'J-Y Mitton', u'Mitton') +
    aliases(u'John Bull', u'J. Bull') +
    aliases(u'Kari Leppänen', u'Kari T. Leppänen', u'Kari T Leppänen', u'Kari Leppänän', u'Kari Läppänen', u'Kari Läppenen', u'K. Leppänen', u'Leppänen') +  
    aliases(u'Karin Bergh', u'K. Bergh') +
    aliases(u'Knut Westad', u'K. Westad', u'Westad') +
    aliases(u'Lee Falk', u'Falk') +
    aliases(u'Leif Bergendorff', u'L. Bergendorff') +
    aliases(u'Lennart Allen', u'L. Allen') +
    aliases(u'Lennart Allen', u'L. Allen') + 
    aliases(u'Lennart Hartler', u'L. Hartler') +
    aliases(u'Lennart Moberg', u'L. Moberg', u'Moberg') +
    aliases(u'Marian J. Dern', u'Marian Dern', u'M. Dern', u'Dern') +  
    aliases(u'Mats Jönsson', u'M. Jönsson') +
    aliases(u'Mats Jönsson', u'Mats Jonsson', u'M. Jonsson') +
    aliases(u'Matt Hollingsworth', u'Hollingsworth') +  
    aliases(u'Mel Keefer', u'M. Keefer', u'Keefer') +
    aliases(u'Michael Jaatinen', u'Mikael Jaatinen', u'M. Jaatinen') +
    aliases(u'Michael Tierres', u'M. Tierres', u'Tierres') +
    aliases(u'Mèziéres', u'Mézières') +	
    aliases(u'Nils Schröder', u'Schröder') +
    aliases(u'Norman Worker', u'N. Worker', u'Worker') +
    aliases(u'Ola Westerberg', u'O. Westerberg') +  
    aliases(u'Patrik Norrman', u'Patrik Norman') +
    aliases(u'PeO Carlsten', u'Peo Carlsten') +
    aliases(u'Peter Sparring', u'P. Sparring') +
    aliases(u'Robert Kanigher', u'Bob Kanigher', u'R. Kanigher') +
    aliases(u'Romano Felmang', u'R. Felmang', u'Felmang', u'Roy Mann', u'Mangiarano') +
    aliases(u'Scott Goodall', u'S. Goodall', u'Goodall', u'Scott Godall') +
    aliases(u'Stefan Nagy', u'S. Nagy') +
    aliases(u'Steve Ditko', u'S. Ditko') +
    aliases(u'Sverre Årnes', u'Årnes') +
    aliases(u'Sy Barry', u'Barry') +
    aliases(u'Terence Longstreet', u'Terrence Longstreet', u'T. Longstreet') +  
    aliases(u'Tina Stuve', u'T. Stuve') +  
    aliases(u'Todd Klein', u'Klein') +
    aliases(u'Tony De Paul', u'Tony DePaul', u'Tony de Paul', u'De Paul', u'DePaul') +  
    aliases(u'Tony De Zuniga', u'Tony de Zuniga') +
    aliases(u'Ulf Granberg', u'U. Granberg', u'Granberg') +
    aliases(u'Usam', u'Umberto Samarini', u'Umberto Sammarini') +  
    aliases(u'William Vance', u'W. Vance', u'Vance') +
    aliases(u'Wilson McCoy', u'Wilson Mc Coy', u'McCoy') +
    aliases(u'Zane Grey', u'Zane Gray', u'Zane Grej') +
    aliases(u'Özcan Eralp', u'Öscan Eralp', u'Ö. Eralp', u'Eralp')
    )

class CreativePart(models.Model):
    episode = models.ForeignKey(Episode)
    creator = models.ForeignKey(Creator)
    alias = models.CharField(max_length=200, blank=True)

    def name(self):
        if self.alias:
            return self.alias
        else:
            return self.creator.name

def CreativePart_create(episode, name):
    if name in ALIASES:
        c = Creator.objects.get_or_create(name=ALIASES[name])[0]
        return CreativePart(episode=episode, creator=c, alias=name)
    else:
        c = Creator.objects.get_or_create(name=name)[0]
        return CreativePart(episode=episode, creator=c)

class Article(models.Model):
    '''Something published that is not an episode of a comic.'''
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200)
    ref_keys = models.ManyToManyField(RefKey)
    
    def __unicode__(self):
        if self.subtitle:
            return u'%s: %s' % (self.title, self.subtitle)
        else:
            return unicode(self.title)
    
class Publication(models.Model):
    issue = models.ForeignKey(Issue)
    episode = models.ForeignKey(Episode, null=True)
    article = models.ForeignKey(Article, null=True)
    ordno = models.PositiveSmallIntegerField(default=4711)

    class Meta:
        ordering = ('issue', 'ordno')
        unique_together = ('issue', 'episode', 'article')
