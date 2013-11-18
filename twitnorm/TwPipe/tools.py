import re
import os
import constants
import CMUTweetTagger
from pymongo import MongoClient
from numpy import array
import pickle
import Levenshtein
import soundex
from stringcmp import editdist_edits, editdist, editex, lcs as LCS
from fuzzy import DMetaphone

vowels = ('a', 'e', 'i', 'o', 'u', 'y')
dims = ['weight', 'lcsr', 'distance', "com chars", "suggestion", "freq"]

CLIENT = MongoClient('localhost', 27017)
DB = CLIENT['tweets']

def top_n(res,n=100,verbose=False):
    in_top_n = 0
    total_ill = 0
    index_list = {}
    for res_ind in range(0,len(res)):
        answer = constants.mapping[res_ind][1]
        ovv = constants.mapping[res_ind][0]
        if answer != ovv:
            total_ill += 1
            if res[res_ind]:
                res_list = [a[0] for a in res[res_ind][:n]]
                if answer in res_list:
                    in_top_n += 1
                    ind = res_list.index(answer)
                    index_list_n = index_list.get(ind,[0,[]])
                    index_list_n[0] += 1
                    index_list_n[1].append(res_ind)
                    index_list[ind] = index_list_n
    print 'Out of %d, %d has an normalization, we^ve %d of those correct normalizations in our list with indexes %s' % (len(res),total_ill, in_top_n,[(a, index_list[a][0]) for a in index_list])
    if verbose:
        for a in index_list:
            if a != 0:
                print  [ (b,a,res[b][a][0]) for b in index_list[a][1]]
    return index_list

def pretty_top_n(res,ind_word,max_val,last=10):
    ind = ind_word
    ovv = constants.mapping[ind_word][0]+"|"+constants.mapping[ind_word][2]
    print "%10.5s %10.6s %10.6s %10.6s %10.6s %10.6s %10.6s" % (ovv, dims[0], dims[1], dims[2], dims[3], dims[4], dims[5],)
    for vec_pre in res[ind][:last]:
        vec = [round(a,4) for a in array(vec_pre[1:len(max_val)+1]) * array(max_val)]
        print "%10.5s %10.6f %10.6f %10.6f %10.6f %10.6f %10.6f" % (vec_pre[0],vec[0],vec[1],vec[2],vec[3],vec[4],vec[5])

def pretty_max_min(res,feat_mat1):
    maxes = max_values(res)[:len(dims)]
    mins = min_values(res)[:len(dims)]
    print "%8.8s %8.8s %8.8s %8.8s %8.8s %8.8s" % (dims[0], dims[1], dims[2], dims[3], dims[4], dims[5],)
    print "%8.6f %8.6f %8.6f %8.6f %8.6f %8.2f" % (mins[0], mins[1], mins[2], mins[3], mins[4], mins[5],)
    print "%8.6f %8.6f %8.6f %8.6f %8.6f %8.2f" % (maxes[0], maxes[1], maxes[2], maxes[3], maxes[4], maxes[5],)

def get_node(word,tag=None,ovv=False):
    if tag is None:
        return [DB.nodes.find_one({'_id':word+"|"+a, 'ovv': ovv }) for a in constants.tags if DB.nodes.find_one({'_id':word+"|"+a})]
    else:
        return DB.nodes.find_one({'_id':word+"|"+tag})

def get_tag(ind,word):
    return constants.mapping[ind][2]

def max_values(res):
    correct_results = []
    for ind in range(0,len(res)):
        if res[ind]:
            if res[ind][0][0] == constants.mapping[ind][1]:
                correct_result = res[ind][0]
                correct_results.append(correct_result[1:])
    arr = array(correct_results)
    return [round(val,6) for val in arr.max(axis=0)]

def min_values(res):
    correct_results = []
    for ind in range(0,len(res)):
        if res[ind]:
            if res[ind][0][0] == constants.mapping[ind][1]:
                correct_result = res[ind][0]
                correct_results.append(correct_result[1:])
    arr = array(correct_results)
    return [round(val,6) for val in arr.min(axis=0)]

def dump_to_file(matrix,filename="matrix2.txt"):
    with open(filename, 'wb') as mfile:
        pickle.dump(matrix,mfile)


def load_from_file(filename="matrix2.txt"):
    with open(filename, 'rb') as mfile:
        matrix = pickle.load(mfile)
    return matrix

def isvalid(w):
    #return true if string contains any alphanumeric keywors
        return bool(re.search('[A-Za-z0-9]', w))

def isMention(w):
    #
    # N @CIRAME --> True
    # P @       --> False
    return len(w) > 1 and w.startswith("@")

def isHashtag(w):
    return w.startswith("#")

def gen_walk(path='.'):
    for dirname, dirnames, filenames in os.walk(path):
        # print path to all subdirectories first.
        #for subdirname in dirnames:
        #            print os.path.join(dirname, subdirname)

        # print path to all filenames.
        for filename in filenames:
            yield os.path.join(dirname, filename)

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if '.git' in dirnames:
            # don't go into any .git directories.
            dirnames.remove('.git')

def build_mappings(results,pos_tagged):
    mapp = []
    for i in range(0,len(results)):
        for (word_ind ,(a,b,c)) in enumerate(constants.results[i]):
            if b == 'OOV':
                tag = pos_tagged[i][word_ind][1]
                mapp.append([a,c,tag])
    return mapp

def distance(ovv,cand):
    ovv = re.sub(r'(.)\1+', r'\1\1', ovv)
    return editdist(ovv,cand)

def common_letter_score(ovv,cand):
    ovv = re.sub(r'(.)\1+', r'\1\1', ovv)
    return float(len(set(ovv).intersection(set(cand)))) / len(set(ovv).union(set(cand)))

def lcsr(ovv,cand):
    lcs = LCS(ovv,cand)
    max_length = max(len(ovv),len(cand))
    lcsr = lcs/max_length
    def remove_vowels(word):
        for vowel in vowels:
            word = word.replace(vowel, '')
    ed = editex(remove_vowels(ovv),remove_vowels(cand))
    simcost = lcsr/ed
    return simcost

def filter_cand(ovv,cand,edit_dis=2,met_dis=1):
    #repetition removal
    #re.sub(r'([a-z])\1+', r'\1', 'ffffffbbbbbbbqqq')
    ovv = re.sub(r'(.)\1+', r'\1\1', ovv)
    #cand = re.sub(r'(.)\1+', r'\1\1', cand)
    try:
        t_c_check = sum(editdist_edits(ovv,cand)[1]) <= edit_dis
        t_p_check = metaphone_distance_filter(ovv,cand,met_dis)
    except Exception, e:
        return False
    return t_c_check and t_p_check

def metaphone_distance_filter(ovv,cand,met_dis):
    met_set_ovv = DMetaphone(4)(ovv)
    met_set_cand = DMetaphone(4)(cand)
    for met in met_set_ovv:
        if met:
            for met2 in met_set_cand:
                if met2:
                    try:
                        dist = sum(editdist_edits(met,met2)[1])
                    except IndexError:
                        dist = sum(editdist_edits(met+".",met2+".")[1])
                    if  dist <= met_dis:
                        return True

    return False

def soundex_distance(ovv_snd,cand):
    try:
        lev = Levenshtein.distance(unicode(ovv_snd),soundex.soundex(cand.decode("utf-8","ignore")))
    except UnicodeEncodeError:
        print 'UnicodeEncodeError[ovv_snd]: %s %s' % (ovv_snd,cand)
        lev = Levenshtein.distance(ovv_snd,soundex.soundex(cand.encode("ascii","ignore")))
    except UnicodeDecodeError:
        print 'UnicodeDecodeError[ovv_snd]: %s %s' % (ovv_snd,cand)
        lev = Levenshtein.distance(ovv_snd,soundex.soundex(cand.decode("ascii","ignore")))
    except TypeError:
        print 'TypeError[ovv_snd]: %s %s' % (ovv_snd,cand)
        lev = 10.
    snd_dis = lev
    return snd_dis
