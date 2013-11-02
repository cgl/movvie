## to fill in the db
import graphlib
graphlib.main('test/snap.sample')

tweets = [u"someone is cold game nd he needs to follow me",
          u"only 3mths left in school . i wil always mis my skull , frnds and my teachrs"]

import CMUTweetTagger ; lot = CMUTweetTagger.runtagger_parse(tweets)

N = normalizer.Normalizer(lot)


reload(normalizer); N = normalizer.Normalizer(lot) ; b= N.normalizeAll()

reload(normalizer);reload(scoring); lot = scoring.bisi()

from pymongo import MongoClient ;client = MongoClient('localhost', 27017);db = client['tweets']
db = client.tweets
db.edges.ensure_index([ ('from', 1), ('to', 1) , ('dis', 1 )] )
