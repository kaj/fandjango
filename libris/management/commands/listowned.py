from django.core.management.base import BaseCommand
from libris.models import *
from collections import defaultdict

class Command(BaseCommand):
    help = 'Simple list of the issues I have.'

    def handle(self, *args, **options):
        data = defaultdict(list)
        for year, number, numberStr in Issue.objects.distinct() \
                                 .filter(publication__ordno__lt=4711) \
                                 .values_list('year', 'number', 'numberStr'):
            if numberStr == '%d' % number:
                data[year].append(int(number));
            elif numberStr == '%d-%d' % (number, number + 1):
                data[year].append(int(number));
                data[year].append(int(number) + 1);
            else:
                raise RuntimeError("Unexpected numberstr %s for nr %d" % (numberStr, number))

        for year, issues in data.items():
            print("%s: %s" % (year, issuestr(issues)))


def issuestr(issues):
    def inner(start, end):
        if start == end:
            return "%d" % start
        else:
            return "%d-%d" % (start, end)

    result = [];
    i = iter(issues);
    start = next(i)
    end = start
    for issue in i:
        if issue != end + 1:
            result.append(inner(start, end))
            start = issue
            end = start
        else:
            end = issue
    result.append(inner(start, end))
    return ", ".join(result)
