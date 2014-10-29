from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

def link(value, linkbase='', autoescape=None):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    if 'get_absolute_url' in dir(value):
        url = value.get_absolute_url()
    else:
        url = linkbase + value.slug
    if 'part_no' in dir(value) and 'part_name' in dir(value):
        if value.part_no and value.part_name:
            extra = ' (del %d: %s)' % (value.part_no, value.part_name)
        elif value.part_no:
            extra = ' (del %d)' % value.part_no
        elif value.part_name:
            extra = ' (%s)' % value.part_name
        else:
            extra = ''
    else:
        extra = ''
    return mark_safe(u'<a href="%s">%s</a>%s' % (url, esc(value), esc(extra)))

@register.filter
def linklist(value, linkbase='', autoescape=None):
    return mark_safe(u', '.join(link(i, linkbase) for i in value))
linklist.needs_autoescape = True

@register.simple_tag
def origtitle(ot):
    if ot:
        return '<p class="i orig">Originaltitel: <q lang="%s">%s</q>.</p>' % (
            ot.language, ot.title)
    else:
        return ''
