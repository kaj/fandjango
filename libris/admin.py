from libris.models import *
from django.contrib import admin

class PublicationInIssue(admin.TabularInline):
    model = Publication
    readonly_fields = ('episode', 'article')

def cover(issue):
    return ', '.join('%s' % by for by in issue.cover_by.all())
cover.admin_order_field = 'cover_by'

class IssueAdmin(admin.ModelAdmin):
    list_display = ('year', 'number', 'pages', 'price', cover, 'cover_best')
    list_display_links = ('year', 'number')
    list_filter = ('year',)
    fieldsets = (
        (None, { 'fields': (('year', 'number'), ('pages', 'price')) }),
        ('Omslag', { 'fields': (('cover_by', 'cover_best'),),
                     'classes': ['collapse'] }),
        )
    inlines = [PublicationInIssue]

class EpisodeAdmin(admin.ModelAdmin):
    def reflist(issue):
        return ', '.join('%s' % k for k in issue.ref_keys.all())
    
    def part(issue):
        if issue.part_no:
            if issue.part_name:
                return u'%d: %s' % (issue.part_no, issue.part_name)
            else:
                return u'%d' % (issue.part_no)
        elif issue.part_name:
            return issue.part_name
        else:
            return ''
    
    list_display = ('title', 'episode', part, reflist)
    list_filter = ('title',)
    filter_horizontal = ('ref_keys',)
    fieldsets = (
        (None, { 'fields':
                     (('title', 'episode'),
                      'orig_name',
                      ('part_no', 'part_name'),
                      'teaser',
                      'note',
                      'ref_keys',
                      ('daystrip'),
                      ('prevpub', 'firstpub'),
                      'copyright') }),
        )
    readonly_fields = ('daystrip', )
    #radio_fields = {'daystrip':admin.HORIZONTAL}
    
    search_fields = ['title__title', 'episode', 'ref_keys__title']
    
admin.site.register(Issue, IssueAdmin)
admin.site.register(Title)
admin.site.register(Episode, EpisodeAdmin)
admin.site.register(RefKey)
admin.site.register(DaystripRun)
