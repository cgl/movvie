## to fill in the db
import graphlib
import soundex
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


ind = 4; matrix = mat2[ind]; ovv = matrix[0]; ovv_snd = soundex.soundex(ovv) ; print ovv ; print len(matrix[1])
for ind_cand in range(0,len(matrix[1])):
    print matrix[1][ind_cand], matrix[2][ind_cand][0], matrix[2][ind_cand][1], matrix[2][ind_cand][2] if matrix[2][ind_cand][2] > 0.1 else 0, Levenshtein.distance(ovv_snd,soundex.soundex(matrix[1][ind_cand]))

reload(analysis); res = analysis.show_results(matrix1,constants.mapping,d1 = 0.4, d2 = 0.1, d3 = 0.5,verbose=False)

with open('matrix.txt', 'wb') as file:
    pickle.dump(matrix1,file)

sss = [matrix1.append(a) for a in mat4]

with open('matrix.txt', 'rb') as file:
    matrix1 = pickle.load(file)

for ind in range(0,len(matrix2)):
    if matrix2[ind][0] != constants.mapping[ind][0]:
        print matrix2[ind][0] , constants.mapping[ind][0]
