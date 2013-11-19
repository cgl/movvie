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
from pymongo import MongoClient
import string
import difflib
import mlpy
import enchant

dic= enchant.Dict("en_US")
vowels = ('a', 'e', 'i', 'o', 'u', 'y')
dims = ['weight', 'lcsr', 'distance', "com chars", "suggestion", "freq"]
chars = string.lowercase + string.digits + string.punctuation
char_ind = [ord(x) for x in chars]
char_map = dict(zip(chars,char_ind))
CLIENT = MongoClient('localhost', 27017)
DB = CLIENT['tweets']

def top_n(res,n=100,verbose=False):
    in_top_n = 0
    total_ill = 0
    index_list = {}
    not_in_list = []
    no_result = []
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
                else:
                    not_in_list.append((res_ind,ovv,answer))
            else:
                no_result.append((res_ind,ovv,answer,constants.mapping[res_ind][2]))
    print 'Out of %d normalization, we^ve %d of those correct normalizations in our list with indexes \n %s' % (total_ill, in_top_n,[(a, index_list[a][0]) for a in index_list])
    if verbose:
        for a in index_list:
            if a != 0:
                print  [ (b,a,res[b][a][0]) for b in index_list[a][1]]
    return index_list,not_in_list, no_result

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

def longest(ovv,cand):
    try:
        ovv_int = [char_map[x] for x in ovv.lower()]
        cand_int = [char_map[y] for y in cand.lower()]
        lcs = mlpy.lcs_std(ovv_int,cand_int)[0]
    except Exception, e:
        print(ovv,cand,e)
        lcs = difflib.SequenceMatcher(None, ovv,cand).find_longest_match(0, len(ovv), 0, len(cand))[2]
    return lcs

def lcsr(ovv,cand):
    ovv = re.sub(r'(.)\1+', r'\1\1', ovv)
    lcs = longest(ovv,cand)
    max_length = max(len(ovv),len(cand))
    lcsr = lcs/max_length
    def remove_vowels(word):
        for vowel in vowels:
            word = word.replace(vowel, '')
    ed = editex(remove_vowels(ovv),remove_vowels(cand))
    simcost = lcsr/ed
    return simcost
def get_suggestions(ovv,ovv_tag):
    ovv = re.sub(r'(.)\1+', r'\1\1', ovv)
    return [word for word in dic.suggest(ovv)
                   if dic.check(word) and len(word)>2 and
                   get_node(word.decode("utf-8","ignore"),tag=ovv_tag) ]

def filter_cand(ovv,cand,edit_dis=2,met_dis=1):
    #repetition removal
    #re.sub(r'([a-z])\1+', r'\1', 'ffffffbbbbbbbqqq')
    ovv = re.sub(r'(.)\1+', r'\1\1', ovv)
    #cand = re.sub(r'(.)\1+', r'\1\1', cand)
    try:
        t_c_check = in_edit_dis(ovv,cand,edit_dis)
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

def get_dict():
    client_tabi = MongoClient("79.123.176.205", 27017)
    client_shark = MongoClient("79.123.177.251", 27017)
    db_tweets = client_shark['tweets']
    db_dict = client_tabi['dictionary']
    cursor = db_tweets.nodes.find({"freq":{"$gt": 100}}).sort("freq",-1)
    print cursor.count()
    for node in cursor:
        word = node['_id'].split("|")[0]
        if db_dict.dic.find_one({"_id":word}) is not None:
            continue
        else:
            try:
                met_set = DMetaphone(4)(word)
            except UnicodeEncodeError:
                print 'UnicodeEncodeError[get_dict]: %s' % (word)
                met_set = DMetaphone(4)(word.encode("ascii","ignore"))
            query = {}
            for met_ind in range(0,len(met_set)):
                if met_set[met_ind]:
                    query["met%d" %met_ind] =  met_set[met_ind]
                else:
                    pass
            if query:
                query["_id"] = word
                query["ovv"] = node['ovv']
                db_dict.dic.insert(query)

def get_slangs():
    slang = {}
    with open('noslang.txt', 'rb') as file:
        for line in file:
            line_splited = line.split("  -")
            slang[line_splited[0].strip()] = line_splited[1].strip()
    return slang

def find_slang(nil,slang):
    i = 0
    slang = get_slangs()
    for a in nil:
        if slang.has_key(a[1]) and slang.get(a[1]).strip() == a[2]: # strip sil
            #print a[1],a[2]
            i+=1
        elif in_edit_dis(a[1],a[2],3):
            print a[1],a[2],editdist_edits(a[1],a[2])
    print i

def in_edit_dis(word1,word2,dis):
    try:
        return sum(editdist_edits(word1,word2)[1]) <= dis
    except IndexError, i:
        return False


def get_from_dict(word,met_map,met_dis=1):
    client_tabi = MongoClient("79.123.176.205", 27017)
    client_shark = MongoClient("79.123.177.251", 27017)
    db_tweets = client_shark['tweets']
    db_dict = client_tabi['dictionary']
    met_word_list = DMetaphone(4)(word)
    for met_word in met_word_list:
        if not met_word:
            continue
        if met_map.has_key(met_word):
            pass
        else:
            all_mets = set(db_dict.dic.distinct('met0')).union(set(db_dict.dic.distinct('met1')))
            all_mets.remove(None)
            for met in all_mets:
                if in_edit_dis(met_word,met,met_dis):
                    met_map[met_word] = met_map.get(met_word,[])
                    met_map[met_word].append(met)
        mets = met_map[met_word] if met_map.has_key(met_word) else []
        cursor = db_dict.dic.find({ "$or": [ {"met0": {"$in" : mets}}, {"met1": {"$in" : mets}}] })
        if cursor:
             return [node["_id"] for node in cursor
                    if in_edit_dis(word,node["_id"],3)] ,met_map

def slang_analysis(slang):
    mapp = constants.mapping
    i = 0
    for tup in mapp:
        multi = False
        correct_answer = False
        ill = False
        sl = None
        ovv = re.sub(r'(.)\1+', r'\1\1', tup[0]).lower()
        if slang.has_key(ovv):
            sl = slang.get(ovv)
            if len(sl.split(" ")) > 1:
                multi = True
            elif  sl  == tup[1]:
                i += 1
                correct_answer = True
            elif tup[0] != tup[1]:
                #print tup[0],tup[1],sl
                ill = True
        print "%s [%s] :\t %s , %r, %r, %r" %(tup[0],tup[1],sl,multi,ill,correct_answer)
    print "Corrected %d word" %i
