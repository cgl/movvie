
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

In [171]: mat_new = analysis.calc_score_matrix(constants.pos_tagged,constants.results,analysis.ovvFunc)

sss = [matrix1.append(a) for a in mat4]

with open('matrix2.txt', 'rb') as file:
    matrix1 = pickle.load(file)

for ind in range(0,len(matrix2)):
    if matrix2[ind][0] != constants.mapping[ind][0]:
        print matrix2[ind][0] , constants.mapping[ind][0]

correct_results = []
for ind in range(0,len(res)):
    if res[ind]:
        if res[ind][0][0] == constants.mapping[ind][1]:
            correct_result = res[ind][0]
            correct_results.append(correct_result[1:])

arr = numpy.array(correct_results)
print arr.max(axis=0)
print arr.max(axis=1)
print arr.max(axis=2)
print arr.max(axis=3)
print arr.max(axis=4)

max = [  0.59405118,   1.        ,   1.        ,  13.        ,   2.94004814]

Kaç tanesi listede var?

i = 0 ; j = 0; index_list = {}
for res_ind in range(0,len(res)):
    answer = constants.mapping[res_ind][1]
    ovv = constants.mapping[res_ind][0]
    if answer != ovv:
        j += 1
        if res[res_ind]:
            res_list = [a[0] for a in res[res_ind]]
            if answer in res_list:
                i += 1
                ind = res_list.index(answer)
                index_list_n = index_list.get(ind,[0,[]])
                index_list_n[0] += 1
                index_list_n[1].append(res_ind)
                index_list[ind] = index_list_n

print 'Out of %d, %d has an normalization, we have %d of those correct normalizations in our list with indexes %s' %(len(res),j,i,[(a, index_list[a][0]) for a in index_list])

kim hangi sırada geliyor:

for a in index_list:
    if a != 0:
        print  [ (b,a,res[b][a][0]) for b in index_list[a][1]]


ones = [1. for a in range (0,len(dims))]

edit_dis=2 ; met_dis=1 ;feat_mat = analysis.iter_calc_lev_sndx(matrix1); feat_mat1 = copy.deepcopy(feat_mat)
 res = analysis.show_results(feat_mat1,constants.mapping, dim=dim , max_val=max_val , verbose=False)

import sys; sys.path.append("/Users/cagil/work/movvie/twitnorm/TwPipe/febrl-0.4.2/")

import sys ; sys.path.append("/home/cagil/repos/movvie/twitnorm/TwPipe/febrl-0.4.2/")
sys.path.append("/usr/lib/python2.7/dist-packages/")

import tools, analysis, constants,copy
matrix1 = tools.load_from_file()
edit_dis=3 ; met_dis=1 ;feat_mat = analysis.iter_calc_lev_sndx(matrix1,edit_dis= edit_dis, met_dis=met_dis)

feat_mat1 = copy.deepcopy(feat_mat)
res = analysis.show_results(feat_mat1,constants.mapping, dim=[0,1,0,0,0,1] , max_val=[0,1,0,0,0,1/1583551.00],verbose=False)

tools.pretty_max_min(res,feat_mat1)
pretty_top_n(res,ind_word,max_val)

index_list,nil,no_res = tools.top_n(res,verbose=True)

edit_dis=2 ; met_dis=1 ;feat_mat = analysis.iter_calc_lev_sndx(matrix1); feat_mat1 = copy.deepcopy(feat_mat)
res = analysis.show_results(feat_mat1,mapp, dim=[0.2, 0.2, 0.2, 0.2, 0., 0.2] , max_val=[1, 1, 1, 1, 0,1/1739259.0])

for rr in index_list[1][1]:
    print rr
    tools.pretty_top_n(res,rr,max_val,last=3)
