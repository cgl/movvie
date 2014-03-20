# -*- coding: utf-8 -*-

import sqlite3 as sqlite
from sqlite3 import IntegrityError
from main.models import Movie as Movvie ,Review
import datetime
import locale
from django.db import IntegrityError

class Movie:
    #Initialize the crawler with the name of the database
    def __init__(self, id,title = "title", url = "", date = "30/2/2012", rating = 3.0):
        self.id = id
        self.title = title
        self.url = url
        self.date = date
        # default IMDb rating is the mean value of [0.0, 10.0]
        self.rating = rating
        self.reviews = []
        try:
            locale.setlocale(locale.LC_ALL,'tr_TR.UTF-8')
        except Exception:
            try:
                locale.setlocale(locale.LC_ALL, 'tr_TR.utf8')
            except Exception as e:
                print("An error occurred: %s " % e)
    def add_review(self,review,star,tarih):
        self.reviews.append({'body': review, 'star': star, 'tarih': tarih})

    def persist(self):
        try:
            date = datetime.datetime.strptime(self.date, "%d/%m/%Y").strftime("%Y-%m-%m")
        except ValueError:
            date = datetime.datetime.today().strftime("%Y-%m-%m")
        except ValidationError:
            date = datetime.datetime.today().strftime("%Y-%m-%m")

        try:
            m,c = Movvie.objects.get_or_create(movvie_id=self.id,title=self.title,release_date=date,url=self.url,rating=self.rating)
            if c:
                m.save()

            for r in self.reviews:
                try:
                    date = datetime.datetime.strptime(r['tarih'], "%d %b %Y-%H.%M")
                except ValueError:
                    date = datetime.datetime.strftime(datetime.datetime.now(), "%d %b %Y-%H.%M")
                try:
                    print m
                    print m.pk
                    Review.objects.create(movie_id=m.pk,body=r['body'],date=date,rating=r['star'])
                except UnicodeDecodeError:
                    print "UnicodeDecodeError"

        except IntegrityError:
            print "IntegrityError: column movvie_id is not unique %d" % self.id


    def persist2(self, dbname = "movie.db"):
        con = sqlite.connect(dbname)
        try:
            query = """INSERT INTO Movie(`movieID`,`title`, `date`, `url`, `rating`) VALUES (%d, '%s' , '%s', '%s', %f)""" % (self.id , self.title.replace("'", "_"), self.date ,self.url,self.rating)
            con.execute(query)
            for r in self.reviews:
                query = "INSERT INTO Review(movie, body, date,rating) VALUES (%d, '%s','%s',  %f)" % ( self.id , r['body'].replace("'", "_"), r['tarih'] ,r['star'] )
                con.execute(query)
        except IntegrityError as e:
            print e
            print "Integrity error()"
        con.commit()
        con.close()
