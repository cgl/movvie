## to fill in the db
import graphlib
graphlib.main('test/snap.sample')

tweets = [u"someone is cold game nd he needs to follow me",
          u"only 3mths left in school . i wil always mis my skull , frnds and my teachrs"]

import CMUTweetTagger ; lot = CMUTweetTagger.runtagger_parse(tweets)

import normalizer, scoring

N = normalizer.Normalizer(lot)

reload(normalizer) ;N = normalizer.Normalizer(lot,database='tweets')

reload(normalizer); N = normalizer.Normalizer(lot) ; b= N.normalizeAll()

reload(normalizer); reload(scoring); sonuc = scoring.bisi()

from pymongo import MongoClient ;client = MongoClient('localhost', 27017);db = client['tweets']

db = client['tweets']

db.edges.ensure_index([ ('from', 1), ('to', 1) , ('dis', 1 )] )
db.edges.ensure_index('from_tag', 1)
db.edges.ensure_index('to_tag', 1)

N.get_neighbours_candidates(lot[0],'nd','&')

N.get_cands_with_weigh_freq('hve' , 'V', 'to', 'from', 'should|V' , 1 )


ind = 4; ovv = mat2[ind][0]; ovv_snd = soundex.soundex(ovv) ; print ovv ; print len(mat[ind][1])
for ind_cand in range(0,len(mat[ind][1])):
    print mat[ind][1][ind_cand], mat[ind][2][ind_cand][0], mat[ind][2][ind_cand][1], mat[ind][2][ind_cand][2] if mat[ind][2][ind_cand][2] > 0.1 else 0, Levenshtein.distance(ovv_snd,soundex.soundex(mat[ind][1][ind_cand]))
