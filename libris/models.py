from django.db import models

class Issue(models.Model):
    '''A single issue'''
    year = models.IntegerField()
    number = models.IntegerField()
    pages = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("year", "number")
    
    def __unicode__(self):
        return u'Fa %s %s' % (self.number, self.year)
 
class Title(models.Model):
    '''A (reocurring) title'''
    title = models.CharField(max_length=200, unique=True)

    def __unicode__(self):
        return u'%s' % (self.title)

class Episode(models.Model):
    '''An episode such as it occurs in an Issue.  This might mean an
    episode of a reoccuring title, a part of such an episode, a
    one-shot or a part of a one-shot.'''
    title = models.ForeignKey(Title)
    episode = models.CharField(max_length=200)
    part_no = models.IntegerField(blank=True, null=True)
    part_name = models.CharField(max_length=200, blank=True)
    teaser = models.TextField(blank=True)

    def __unicode__(self):
        if self.part_no:
            return u'%s: %s del %s: %s' % (self.title, self.episode,
                                           self.part_no, self.part_name)
        else:
            return u'%s: %s' % (self.title, self.episode)
        
class Publication(models.Model):
    issue = models.ForeignKey(Issue)
    episode = models.ForeignKey(Episode)
    ordno = models.IntegerField()
