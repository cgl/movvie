"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from main.models import Movie as Movvie ,Review
import Movie

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def setUp(self):
        film_id = 190918
        film_title = u"12.Zincirsiz"
        film_url = u"http://www.beyazperde.com/filmler/film-190918/kullanici-elestirileri/en-yeniler/?page=%d"
        m = Movie.Movie(film_id,film_title,film_url)
        m.persist()

    def test_movvie(self):
        mov = Movvie.objects.get(movvie_id= 190918)
        self.assertEqual(mov.title ,  u"12.Zincirsiz")
