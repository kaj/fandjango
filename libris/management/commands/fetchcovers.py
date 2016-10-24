from PIL import Image
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand
from libris.models import Issue
from os import makedirs, path
from urllib.parse import urljoin
from urllib.request import urlopen, urlretrieve

class Command(BaseCommand):
    help = 'Fetch cover images from phantomwiki'

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        self.wikibase = 'http://www.phantomwiki.org/'
        self.staticdir = settings.STATIC_ROOT

        for issue in Issue.objects.all():
            try:
                self.fetchcover(issue.numberStr, issue.year)
            except Exception as x:
                self.log(1, "Error handling %s: %s", issue, x)

    def fetchcover(self, nr, year):
        filename = path.join(self.staticdir, "c%s/m%s.jpg" % (year, nr))
        if path.exists(filename):
            self.log(3, "Cover for %s, %s exists", nr, year)
        else:
            self.log(2, "Should fetch cover for %s, %s", nr, year)
            page1 = self.open_soup("/Fantomen_%s/%s" % (nr, year))
            url = page1.select_one("#bodyContent a.image").attrs['href']
            if 'Scullmark.gif' in url:
                raise RuntimeError("Cover missing for %s, %s" % (nr, year))
            self.log(3, "Image page url is %s", url)
            page = self.open_soup(url)
            url = self.wikiurl(page.select_one(".fullImageLink a").attrs['href'])
            self.log(3, "Image url: %s", url)
            makedirs(path.dirname(filename), exist_ok=True)
            urlretrieve(url, filename)
        smallfile = path.join(self.staticdir, "c%s/s%s.jpg" % (year, nr))
        if not path.exists(smallfile):
            self.log(2, "Should thumbnail %s to %s", filename, smallfile)
            img = Image.open(filename)
            img.thumbnail((220, 220), resample=Image.LANCZOS)
            img.save(smallfile)
            self.log(1, "Stored cover(s) for %s, %s", nr, year)

    def log(self, level, fmt, *args):
        if self.verbosity >= level:
            print(fmt % args)

    def open_soup(self, url):
        return BeautifulSoup(urlopen(self.wikiurl(url)), "lxml")

    def wikiurl(self, url):
        return urljoin(self.wikibase, url)
