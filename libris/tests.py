# -*- encoding: utf-8 -*-
"""
Tests for fandjango.
"""

from django.test import TestCase, Client

class PageTest(TestCase):
    def test_front_page(self):
        self.assertContains(Client().get('/'), 'Fantomenindex')

    def test_titles_page(self):
        self.assertContains(Client().get('/titles'),
                            'Serier i Fantomentidningen')
    def test_key_page(self):
        self.assertContains(Client().get('/what/'), 'Fantomens värld')

    def test_creators_page(self):
        self.assertContains(Client().get('/who/'),
                            'Serieskapare i Fantomentidningen')

    def test_notfound(self):
        self.assertContains(Client().get('/whatever'),
                            'Du hittar inte Fantomen', status_code=404)
