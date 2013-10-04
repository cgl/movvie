#-*- coding: utf-8 -*-
import datetime, urllib2,re
from BeautifulSoup import BeautifulSoup
import Movie
import sqlite3 as sqlite
from sqlite3 import OperationalError
today = datetime.date.today()
title_url = "http://www.beyazperde.com/filmler/tum-filmleri/kullanici-puani/onyil-2010/?page=%d"
base_url = "http://www.beyazperde.com"
counter=0
'''
for s in soup.findAll(href=re.compile("filmler/film-[0-9]*\/$")):
    s.attrMap['href']
'''
def on_yil(start_page=1):
    # Browse though the movie list paging is 20 movie
    for i in range(start_page,2):
        c = urllib2.urlopen(title_url %i)
        soup = BeautifulSoup(c.read())
        div_content = soup.findAll("div","content")
        page(div_content)
        print "End of page %d" %i

def page(content):
    for s in content:
        try:
            h = s('div')[0]('a')[0]['href']
            film_title = s('div')[0].getText()
#Out[126]: u'/filmler/film-132874/'
            film_id = int(h.split('/')[2].split('-')[1])
            film_url = base_url+h+"kullanici-elestirileri/en-yeniler/?page=%d"
            m = Movie.Movie(film_id,film_title,film_url)
            film_html = get_html(film_url %1)
            movie = get_elestiri(film_html,m)
            pager = film_html.find("div","pager")
            if pager:
                li = pager('li')
                li.reverse()
                if li and li[0].span:
                    for i in range(2,int(li[0].span.text)+1):
                        movie = get_elestiri(get_html(film_url %i),movie)
                else:
                    if li and li[0].a['href']:
                        movie = get_elestiri(get_html(li[0].a['href']),m)
                    else:
                        print 'error on %s' %film_url
            if len(m.reviews)>0:
                m.persist()
                print counter
        except IndexError:
            print "IndexError"
            print s

def get_elestiri(film_html,movie):
    global counter
    for e in film_html.findAll("div","box_07"):
        elestiri = e.p.getText()
        name = e.contents[3]('span')[0].getText()
        star = e.contents[3]('span')[1].getText()
        counter += 1
        star = float(star.split('-')[0].strip('&nbsp;'))
        regex = re.match(r".*(?P<tarih>\d{2} .* \d{4}).*(?P<saat>\d{2}.\d{2})", e.find('span','fs11').getText())
        if  regex:
            tarih = regex.group('tarih')+'-'+regex.group('saat')
        else:
            print e.find('span','fs11').getText()
            print movie.id
            tarih = ''
            print 'Tarih error'
        movie.add_review(elestiri,star,tarih)
    return movie
        # u'&nbsp;5 - Ba\u015fyap\u0131t'

def get_html(url):
    if not url.startswith('http'):
        url = base_url + url
    f_o = urllib2.urlopen(url)
    film_html = BeautifulSoup(f_o.read())
    return film_html
    # u'/filmler/film-132874/kullanici-elestirileri/en-yeniler/?page=2

def create_db(dbname = "movie.db"):
    # Create the tables required for the movie database
    con = sqlite.connect(dbname)
    con.execute('CREATE TABLE Movie(movieID INTEGER PRIMARY KEY, title, \
       date DATE, url, rating DOUBLE)')
    #       original_title, mtime, mdate DATE, url, channel, imdb_rating DOUBLE, isWatch INTEGER)')
    con.execute('CREATE INDEX Movieidx on Movie(movieID)')
    con.execute('CREATE TABLE Review(reviewID INTEGER PRIMARY KEY AUTOINCREMENT, movie,body, date, rating FLOAT)')
    con.commit()
    con.close()

def update_db(dbname = "movie.db",table='Sentence'):
    # Update the Sample table by asking the user if the Sentence is po or neg or neutral
    # http://initd.org/pub/software/pysqlite/doc/usage-guide.html#using-shortcut-methods
    isPos = {}
    con = sqlite.connect(dbname)
    con.row_factory = sqlite.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM %s where sentiment = 99" %table) #order by random()
    for row in cur:
        print('\n %d : %s ' %(row["reviewID"],row["body"]))
        result = raw_input(u"Positif mi Negatif mi, Tarafsiz mi (Pozitif/Negatif/Tarafsiz/Oylama): ")
        if (result.upper().strip() == 'P'):
            isPos[row["sentenceID"]] = 1
        elif (result.upper().strip()  == 'N'):
            isPos[row["sentenceID"]] = -1
        elif (result.upper().strip()  == 'O'):
            isPos[row["sentenceID"]] = -99
        elif (result.upper().strip()  == 'B'):
            break
        elif(result.upper().strip()  == 'T'):
            isPos[row["sentenceID"]] = 0  
        else:
            pass

    for key, value in isPos.iteritems():
        con.execute("UPDATE %s SET sentiment = %s WHERE sentenceID = %s" % (table,value, key))
        con.commit()
    con.close()

def create_table(dbname = "movie.db", table='Sentence'):
    # Create the tables required for the movie database
    con = sqlite.connect(dbname)
    try:
        con.execute('drop table %s' %table)
        con.commit()
    except OperationalError:
        print 'Could not drop the table'
    con.execute('CREATE TABLE %s(sentenceID INTEGER PRIMARY KEY AUTOINCREMENT,  reviewID, movieID ,body, rating FLOAT, sentiment INTEGER )' %table)
    con.commit()
    con.close()

def select_reviews(dbname = "movie.db", table = 'Sentence'):
    con = sqlite.connect(dbname)
    con.row_factory = sqlite.Row
    cur = con.cursor()

    for r in map( lambda x: x / 2.0 , range(0 ,11 , 1)):
        print r
        cur.execute("SELECT * from Review where rating = %f order by random() limit 30" %r)

        for row in cur:
#            review = re.sub(r'(?P<sayi>[0-9]+)\.(?P<sayi2>[0-9]+)', r'\g<sayi>,\g<sayi2>',row['body'])
            review_pre = re.sub(r'(?P<sayi>[0-9]+)\.', r'\g<sayi>,',row['body'])
            review = re.sub(r'(?P<abr>\ [A-Z][A-Z]?)\.', r'\g<abr>,',review_pre)
            splitted_review = re.findall("[A-Za-z].*?[\.!?..]", review, re.MULTILINE | re.DOTALL | re.U )
            if len(splitted_review) > 0:
                for rev in splitted_review:
                    insert_sentence(row,rev,cur,con,table)
            else:
                insert_sentence(row,rev,cur,con,table)
    con.close()


def insert_sentence(row,review,cur,con,table):
    print row['movieID']
    cur.execute("SELECT * FROM %s where reviewID=%d" %('Sentence',row['movieID']))
    if len(cur.fetchmany()) == 0:
        try:
            query = """INSERT INTO %s(`reviewID`, `movieID`,`body`, `rating`, `sentiment` ) VALUES (%d, '%d', '%s', %f , %d)""" % ( table, row['movieID'] , row['movie'], review , row['rating'] , 99 )
            con.execute(query)
            con.commit()
        except TypeError:
            import pdb
            pdb.set_trace()            
    else:
        print 'Review exist %s' %row['movieID']
