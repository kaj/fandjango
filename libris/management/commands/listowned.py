from django.core.management.base import BaseCommand
from libris.models import *

class Command(BaseCommand):
    help = 'Simple list of the issues I have.'

    def handle(self, *args, **options):
        prevyear = None
        issues = []
        for year, number in Issue.objects.distinct() \
                                 .filter(publication__ordno__lt=4711) \
                                 .values_list('year', 'number'):
            if year != prevyear:
                if prevyear:
                    print "%s: %s" % (prevyear, issuestr(issues))
                prevyear = year
                issues = []
            if len(issues) == 0:
                issues.append([number,number])
            elif issues[-1][1] == (number-1):
                issues[-1][1] = number
            else:
                issues.append([number,number])
            
        print "%s: %s" % (prevyear, issuestr(issues))


def issuestr(issues):
    return ', '.join('%s' % p[0] if p[0]==p[1] else '%s-%s' % (p[0], p[1])
                     for p in issues)
