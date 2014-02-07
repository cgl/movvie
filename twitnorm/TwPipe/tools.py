import re
import os
import constants
import CMUTweetTagger
from pymongo import MongoClient
from numpy import array
import pickle
import Levenshtein
import soundex
from stringcmp import editdist_edits, editdist, editex
from fuzzy import DMetaphone
import string
import difflib
import mlpy
import enchant

units = ["zero", "one", "to", "three", "for",  "five","six", "seven", "eight", "nine"]
units_in_oov = ["o","one","to","three","for","five","six", "seven", "eight", "nine"]
units_in_word = ["o",("one","l"),"to", "e", ("for","fore","a") , "s",  "b",  "t", "ate", "g"]
pronouns = {u'2':u"to",u'w':u"with",u'4':u'for'}

#mapp = constants.mapping
dic= enchant.Dict("en_US")
vowels = ('a', 'e', 'i', 'o', 'u', 'y')
dims = ['weight', 'lcsr', 'distance', "com chars", "slang", "freq", "result"]
chars = string.lowercase + string.digits + string.punctuation
char_ind = [ord(x) for x in chars]
char_map = dict(zip(chars,char_ind))
CLIENT = MongoClient('localhost', 27017)
try:
    db_tweets = CLIENT['tweets2']
    db_dict = CLIENT['dictionary2']
except:
    db_tweets  = None

def build_mappings(results,pos_tagged,oov_fun):
    mapp = []
    for i in range(0,len(results)):
        for (word_ind ,(org_word,w_type,ann_word)) in enumerate(results[i]):
            if oov_fun(org_word,w_type,ann_word):
                tag = pos_tagged[i][word_ind][1]
                acc = pos_tagged[i][word_ind][2]
                mapp.append([org_word,ann_word,tag,acc])
    return mapp
#ann_and_pos_tag = build_mappings(constants.results,constants.pos_tagged)


def spell_check(word):
    if len(word) > 1 :
        return dic.check(word) or dic.check(word.capitalize())
    elif word in [u"a", u"i"]:
        return True
    else:
        return False

def top_n(res,not_ovv,mapp,ann_and_pos_tag,n=100,verbose=False):
    in_top_n = 0
    total_ill = 0
    index_list = {}
    not_in_list = []
    no_result = []
    for res_ind in range(0,len(res)):
        correct_answer = mapp[res_ind][1]
        ovv = mapp[res_ind][0]
        if not_ovv and not_ovv[res_ind]:
            if correct_answer.lower() == not_ovv[res_ind].lower():
                pass
            elif verbose:
                print "Houston",res_ind, ovv,correct_answer, not_ovv[res_ind]
        elif correct_answer != ovv:
            total_ill += 1
            if res[res_ind]:
                res_list = [a[0].lower() for a in res[res_ind][:n]] # lower
                if correct_answer.lower() in res_list:
                    in_top_n += 1
                    cor_ind = res_list.index(correct_answer.lower())
                    index_list_n = index_list.get(cor_ind,[0,[]])
                    index_list_n[0] += 1
                    index_list_n[1].append(res_ind)
                    index_list[cor_ind] = index_list_n
                else:
                    not_in_list.append((res_ind,ovv,correct_answer,mapp[res_ind][2],ann_and_pos_tag[res_ind][3]))
            else:
                no_result.append((res_ind,ovv,correct_answer,mapp[res_ind][2],ann_and_pos_tag[res_ind][3]))
    print 'Out of %d normalization, we^ve %d of those correct normalizations in our list with indexes \n %s' % (total_ill, in_top_n,[(a, index_list[a][0]) for a in index_list])
    if verbose:
        for a in index_list:
            if a != 0:
                print  [ (b,a,res[b][a][0]) for b in index_list[a][1]]
    return index_list,not_in_list, no_result

def pretty_top_n(res,ind_word,mapp,max_val,last=10):
    ind = ind_word
    ovv = mapp[ind_word][0]+"|"+mapp[ind_word][2]
    print "%10.10s %10.6s %10.6s %10.6s %10.6s %10.6s %10.6s %10.6s Current res" % (ovv, dims[0], dims[1], dims[2], dims[3], dims[4], dims[5],dims[6])
    for vec_pre in res[ind][:last]:
        vec = [round(a,4) for a in array(vec_pre[1:len(max_val)+1]) * array(max_val)]
        print "%10.10s %10.6f %10.6f %10.6f %10.6f %10.6f %10.6f %10.6f %10.6f"  % (vec_pre[0],vec[0],vec[1],vec[2],vec[3],vec[4],vec[5],vec_pre[-1],sum(vec))

def pretty_max_min(res,feat_mat1,mapp):
    maxes = max_values(res,mapp)
    mins = min_values(res)
    print "%8.8s %8.8s %8.8s %8.8s %8.8s %8.8s %8.8s " % (dims[0], dims[1], dims[2], dims[3], dims[4], dims[5],dims[6],)
    print "%8.6f %8.6f %8.6f %8.6f %8.6f %8.2f %8.6f" % (mins[0], mins[1], mins[2], mins[3], mins[4], mins[5], mins[6],)
    print "%8.6f %8.6f %8.6f %8.6f %8.6f %8.2f %8.6f" % (maxes[0], maxes[1], maxes[2], maxes[3], maxes[4], maxes[5],maxes[6],)

def pretty_incorrects(incor,mapp):
    for ind,ans in incor:
        print "%4d  %10s %10s %10s" %(ind, mapp[ind][0], mapp[ind][1], ans)

def get_node(word,tag=None,ovv=False):
    word = word.lower()
    if tag is None:
        return [node for node in db_tweets.nodes.find({'node':word, 'ovv': ovv }).sort("freq",-1)]
    else:
        return db_tweets.nodes.find_one({'node':word, "tag":tag})

def get_tag(ind,word,mapp):
    return mapp[ind][2]

def max_values(res,mapp):
    correct_results = []
    for ind in range(0,len(res)):
        if res[ind]:
            if res[ind][0][0] == mapp[ind][1]:
                correct_result = res[ind][0]
                correct_results.append(correct_result[1:])
    arr = array(correct_results)
    return [round(val,6) for val in arr.max(axis=0)]

def min_values(res,mapp):
    correct_results = []
    for ind in range(0,len(res)):
        if res[ind]:
            if res[ind][0][0] == mapp[ind][1]:
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


def parseTweets(tweets):
    lot = CMUTweetTagger.runtagger_parse(tweets)
    return lot

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

def distance(ovv,cand):
    ovv = get_reduced(ovv)
    return editdist(ovv,cand)

def common_letter_score(ovv,cand):
    ovv = get_reduced(ovv)
    return float(len(set(ovv).intersection(set(cand)))) / len(set(ovv).union(set(cand)))

def longest(ovv,cand):
    try:
        ovv_int = [char_map[x] for x in ovv.encode('ascii',"ignore").lower()]
        cand_int = [char_map[y] for y in cand.encode('ascii',"ignore").lower()]
        lcs = mlpy.lcs_std(ovv_int,cand_int)[0]
    except Exception, e:
        print(ovv,cand,e)
        lcs = difflib.SequenceMatcher(None, ovv,cand).find_longest_match(0, len(ovv), 0, len(cand))[2]
    return lcs

def lcsr(ovv,cand):
    ovv = get_reduced(ovv)
    lcs = longest(ovv,cand)
    max_length = max(len(ovv),len(cand))
    lcsr = float(lcs)/max_length
    def remove_vowels(word):
        for vowel in vowels:
            word = word.replace(vowel, '')
    ed = editex(remove_vowels(ovv),remove_vowels(cand))
    simcost = lcsr/ed
    return simcost

def get_suggestions(ovv,ovv_tag):
    ovv = get_reduced(ovv)
    return [word for word in dic.suggest(ovv)
                   if dic.check(word) and len(word)>2 and filter_cand(ovv,word) and
                   get_node(word.decode("utf-8","ignore"),tag=ovv_tag) ]

def filter_cand(ovv,cand,edit_dis=2,met_dis=1):
    #repetition removal
    ovv = get_reduced(ovv)
    try:
        t_c_check = in_edit_dis(ovv.encode('ascii',"ignore"),cand,edit_dis)
        t_p_check = metaphone_distance_filter(ovv.encode('ascii',"ignore"),cand,met_dis)
    except Exception:
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
    cursor = db_tweets.nodes.find({"ovv":False,"freq":{"$gt": 100}}).sort("freq",-1)
    print cursor.count()
    for node in cursor:
        word = node['node']
        if db_dict.dic.find_one({"ovv":False,"node":word}) is not None:
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
                query["node"] = word
                query["ovv"] = node['ovv']
                db_dict.dic.insert(query)

def get_hb_dict():
    hb_dict = {}
    with open('emnlp_dict.txt', 'rb') as file:
        for line in file:
            line_splited = line.split("  ")
            hb_dict[line_splited[0].strip()] = line_splited[1].strip()
    return hb_dict

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
    except IndexError:
        return False


def get_from_dict_met(word,met_map,met_dis=1):
    word = get_reduced(word)
    met_word_list = DMetaphone(4)(word)
    cands = []
    for met_word in met_word_list:
        if not met_word:
            continue
        if met_map.has_key(met_word):
            pass
        else:
            all_mets = set(db_dict.dic.distinct('met0')).union(set(db_dict.dic.distinct('met1')))
            try:
                all_mets.remove(None)
            except KeyError:
                pass
            for met in all_mets:
                if in_edit_dis(met_word,met,met_dis):
                    met_map[met_word] = met_map.get(met_word,[])
                    met_map[met_word].append(met)
        mets = met_map[met_word] if met_map.has_key(met_word) else []
        cursor = db_dict.dic.find({ "ovv":False, "$or": [ {"met0": {"$in" : mets}}, {"met1": {"$in" : mets}}] })
        if cursor:
             cands.extend([node["node"] for node in cursor
                    if in_edit_dis(word,node["node"],3)])
    return cands

def get_from_dict_dis(word,tag,clean_words,distance):

    cands = [cand for cand in clean_words[tag] if in_edit_dis(word,cand,distance)] if clean_words.has_key(tag) else []
    return cands

def get_reduced(word,count=2):
    replace = r'\1\1'
    if count == 1:
        replace = r'\1'
    return re.sub(r'(.)\1+', replace, word.lower())

def get_reduced_alt(word,count=2):
    red1 = get_reduced(word)
    red2 = get_reduced(word,count=1)
    if len(red2) == 1:
        return None
    red1_node = db_tweets.nodes.find_one({'node':red1, "ovv":False ,'freq' : {'$gt':100}})
    red2_node = None
    red2_freq = 0
    red1_freq =  red1_node['freq'] if  red1_node else 0
    if red1 != red2:
        red2_node = db_tweets.nodes.find_one({'node':red2, "ovv":False, 'freq' : {'$gt':100}})
        red2_freq =  red2_node['freq'] if  red2_node else 0
    if red1_node or red2_node:
        return red1_node['node'] if red1_freq >= red2_freq else red2_node['node']
    else:
        return None

def replace_digits(ovv_word):
    if ovv_word.isdigit() and len(ovv_word) == 1:
        ovv_word = units[int(ovv_word)]
    else:
        m = re.search("(-?\d+)|(\+1)", ovv_word)
        if m and len(m.group(0)) == 1 :
            #ovv_word = re.sub("(-?\d+)|(\+1)", lambda m: [units_in_word[int(m.group(0))] if len(m.group(0)) == 1 else m.group(0)], ovv_word
            trans = units_in_oov[int(m.group(0))]
            ovv_word = ovv_word.replace(m.group(0),trans)
    return ovv_word

def replace_digits_alt(oov_word):
    digited = replace_digits(oov_word)
    dig_node = db_tweets.nodes.find_one({'node':digited, "ovv":False, 'freq' : {'$gt':100}})
    return digited if dig_node else None

def slang_analysis(slang,mapp):
    i = 0
    for tup in mapp:
        multi = False
        correct_answer = False
        ill = False
        sl = None
        ovv = get_reduced(tup[0])
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

def get_performance(correct,not_found,incorrect,total_not_ill):
    recall = float(correct)/total_not_ill
    precision = float(correct)/(total_not_ill - not_found)
    fmeasure = 2 * precision * recall / (precision+recall)
    print "Correct: %d , Not Found: %d, Incorrect: %d " %(correct, not_found,incorrect)
    print "Recall: %f , Precision:%f , FMeasure:%f" %(round(recall,3),round(precision,3),round(fmeasure,3))

def get_clean_words():
    words = {}
    for tag in constants.tags:
        cursor = db_tweets.nodes.find({"ovv":False,"tag":tag,"freq":{"$gt": 100}}).sort("freq",-1)
        words[tag] = set()
        for node in cursor:
            word = node['node']
            if len(word) > 2:
                words[tag].add(word)
    return words

def get_score_threshold(index_list,res):
    scores = []
    for ans_ind in index_list.keys():
        for res_ind in index_list[ans_ind][1]:
            scores.append(res[res_ind][ans_ind][-1])
    print "Minimum score: %f , Maximum score: %f" %(min(scores),max(scores))
    return min(scores)

def freq_zero_correct_answers(index_list,res,threshold):
    kucukler = []
    for ans_ind in index_list.keys():
        for res_ind in index_list[ans_ind][1]:
            if res[res_ind][ans_ind][6] < threshold:
                kucukler.append((res_ind,ans_ind,res[res_ind][ans_ind]))
    print "There is %d results with smaller freq than %d " %(len(kucukler),threshold)
    return kucukler


def test_threshold(res,threshold):
    buyukler = 0
    kucukler = 0
    for res_list in res:
        for res_line in res_list:
            score = res_line[-1]
            if score < threshold:
                kucukler += 1
            else:
                buyukler += 1
    print "There is %d result below and %d result above the threshold" %(kucukler,buyukler)

def show_nth_index(ind,index_list,res,mapp,max_val,last=4):
    for rr in index_list[ind][1]:
        print rr,mapp[rr]
        pretty_top_n(res,rr,mapp,max_val,last=last)

def create_extended_mapp(results,not_oov):
    i = 0
    mapp_ext = []
    for ind,tweet in enumerate(results):
        for word in tweet:
            if word[1] == "OOV":
                if not not_oov[i]:
                    mapp_ext.append((ind,word[0]))
                i += 1
    return mapp_ext
