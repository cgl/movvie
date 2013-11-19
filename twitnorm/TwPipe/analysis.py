from scoring import han
import enchant
from fuzzy import DMetaphone
import normalizer
import soundex
import Levenshtein
import CMUTweetTagger
import enchant
import tools
import mlpy
import re
import copy
import traceback

tweets,results = han(548)
ovvFunc = lambda x,y : True if y == 'OOV' else False
dic= enchant.Dict("en_US")
units = ["", "one", "two", "three", "four",  "five",
    "six", "seven", "eight", "nine "]
slang = tools.get_slangs()

import logging


logger = logging.getLogger('analysis_logger')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('analysis.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(fh)
logger.propagate = False
#FORMAT = '%(asctime)-12s (%(process)d) %(message)s'

def main(index=False):
    results = han(548)[1]
    ovv = lambda x,y : True if y == 'OOV' else False
    in_suggestions(results,ovv,index_count=index)

if __name__ == "__main__ ":
    main()

def find_more_results(ovv,ovv_tag):
    cands = []
    try:
        cands,met_map = tools.get_from_dict(ovv,{})
    except IndexError, e:
        print ovv,"IndexError",e
    except TypeError, e:
        print "No new cand for %s" %ovv
    scores = []
    for cand in cands:
        scores.append(get_score_line(cand,0,ovv,ovv_tag))
    return scores

def calc_lev_sndx(mat,ind,edit_dis=2,met_dis=1,verbose=True):
    result_list = []
    matrix = mat[ind]
    ovv = matrix[0].encode('utf-8')
    ovv_tag = tools.get_tag(ind,ovv)
    ovv_snd = soundex.soundex(ovv)
    length = len(matrix[1])
    #suggestions = tools.get_suggestions(ovv,ovv_tag)

    if verbose:
        print '%s: found %d candidate' %(ovv,length)
    result_list = get_candidates_from_graph(matrix,ovv,ovv_tag,edit_dis,met_dis)
    if not result_list:
        result_list = find_more_results(ovv,ovv_tag)

    #    print ovv,suggestions
    result_list.sort(key=lambda x: -float(x[1]))
    return result_list

def get_candidates_from_graph(matrix,ovv,ovv_tag,edit_dis,met_dis):
    result_list = []
    for cand in [cand for cand in matrix[1]
                 if tools.filter_cand(ovv,cand,edit_dis=edit_dis,met_dis=met_dis)]:
        sumof = 0.
        for a,b in matrix[2][matrix[1].index(cand)]:
            sumof += a[0]/a[1]
        line = get_score_line(cand,sumof,ovv,ovv_tag)
        result_list.append(line)
    return result_list

def get_score_line(cand,sumof,ovv,ovv_tag):
    node =  tools.get_node(cand,tag=ovv_tag)
    freq = node['freq'] if node else 0.
    line = [ #cand,
            sumof,                                # weight
            tools.lcsr(ovv,cand),                 # lcsr
            tools.distance(ovv,cand),             # distance
            tools.common_letter_score(ovv,cand),  # shared letter
            0,                                    # 7 : is_in_slang
            freq,
    ]
    for ind in range(0,len(line)):
        line[ind] = round(line[ind],8)
    return line

def iter_calc_lev_sndx(mat,edit_dis=2,met_dis=1,verbose=False):
    mat_scored = []
    for ind in range (0,len(mat)):
        res_list = calc_lev_sndx(mat,ind,verbose=verbose)
        mat_scored.append(res_list)
    return mat_scored

def is_ovv(slang):
    from constants import mapping as mapp
    not_ovv = []
    for ind in range (0,len(mapp)):
        ovv = mapp[ind][0]
        ovv_reduced = re.sub(r'(.)\1+', r'\1', ovv).lower()
        if dic.check(ovv.capitalize()):
            not_ovv.append(ovv.capitalize())
        elif slang.has_key(ovv_reduced):
            sl = slang.get(ovv_reduced)
            if len(sl.split(" ")) >  1:
                not_ovv.append(ovv)
            else:
                not_ovv.append('')
        elif ovv.isdigit():
            not_ovv.append(ovv)
        elif not ovv.isalnum():
            not_ovv.append(ovv)
        else:
            not_ovv.append('')
    i = 0
    for ind,words in enumerate(mapp):
        if words[0] == words[1]:
            if not not_ovv[ind]:
                i+=1
    print i," found"
    return not_ovv


def add_slangs(mat,mapp,slang):
    res_mat = []
    for ind in range (0,len(mat)):
        ovv = mat[ind][0]
        ovv_reduced = re.sub(r'(.)\1+', r'\1\1', ovv).lower()
        cands = {}
        if slang.has_key(ovv_reduced):
            sl = slang.get(ovv_reduced)
            if len(sl.split(" ")) <=  1:
                ovv_tag = mapp[ind][2]
                res_line = get_score_line(sl,0,ovv,ovv_tag)
                res_line[4] = 1
                cands[sl] = res_line
                print ind,ovv,"[",mapp[ind][1],"]",sl,cands[sl]
        res_mat.append(cands)
    return res_mat

def show_results(res_mat,mapp, not_ovv = is_ovv(slang),dim = [ 0.2, 0.2, 0.2, 0.2 , 0.2, 0.2], max_val = [1,1,1,1,1,1/1739259.0], verbose=False):
    results = []
    pos = 0
    slang = tools.get_slangs()
    for ind in range (0,len(res_mat)):
        correct = False
        if not_ovv and not_ovv[ind]:
            res_list = [[not_ovv[ind],0,0,0,0,0,0]]
        else:
            res_dict = copy.deepcopy(res_mat[ind])
            res_list = []
            if res_dict:
                for res_ind,cand in enumerate(res_dict):
                    score = calculate_score(res_dict[cand],dim,max_val)
                    res_dict[cand].append(round(score,7))
                    res_list.append([cand])
                    res_list[res_ind].extend(res_dict[cand])
                res_list.sort(key=lambda x: -float(x[-1]))
        answer = res_list[0][0] if res_list else mapp[ind][0]
        correct_answer = mapp[ind][1]
        if answer == correct_answer or answer.lower() == correct_answer.lower() : #lower
            correct = True
            pos += 1
        if verbose:
            print '%d. %s | %s [%s] :%s' % (ind, 'Found' if correct else '', mapp[ind][0],mapp[ind][1],res_list[0][0])
        results.append(res_list)
    print 'Number of correct answers %s' % pos
    return results


def calculate_score(res_vec,dim,max_val):
    try:
        score  = dim[0] * res_vec[0] * max_val[0]  # weight
        score += dim[1] * res_vec[1] * max_val[1]  # lcsr
        score += dim[2] * res_vec[2] * max_val[2]  # distance
        score += dim[3] * res_vec[3] * max_val[3]  # common letter
        score += dim[4] * res_vec[4] * max_val[4]  # slang
        score += dim[5] * res_vec[5] * max_val[5]  # freq
        return score
    except IndexError, i:
        print res_vec,i
    except TypeError, e:
        print res_vec
        print traceback.format_exc()

def calc_score_matrix(lo_postagged_tweets,results,ovvFunc):
    logger.info('Started')
    lo_candidates = []
    norm = normalizer.Normalizer(lo_postagged_tweets,database='tweets')
    for tweet_ind in range(0,len(lo_postagged_tweets)):
        tweet_pos_tagged = lo_postagged_tweets[tweet_ind]
        for j in range(0,len(tweet_pos_tagged)):
            word = results[tweet_ind][j]
            if ovvFunc(word[0],word[1]):
                ovv_word = word[0]
                ovv_tag = tweet_pos_tagged[j][1]
                keys,score_matrix = norm.get_candidates_scores(tweet_pos_tagged,ovv_word,ovv_tag)
                lo_candidates.append([ovv_word,keys,score_matrix])
    logger.info('Finished')
    return lo_candidates

def calc_each_neighbours_score(tweets_str, results, ovv):
    lo_tweets = CMUTweetTagger.runtagger_parse(tweets_str)
    lo_candidates = []
    norm = normalizer.Normalizer(lo_tweets,database='tweets')
    for i in range(0,len(results)):
        tweet = results[i]
        tweet_pos_tagged = CMUTweetTagger.runtagger_parse([tweets[i]])[0] # since only 1 tweet
        for j in range(0,len(tweet)):
            word = tweet[j]
            if ovv(word[0],word[1]):
                ovv_word = word[0]
                ovv_tag = tweet_pos_tagged[j][1]
                candidates = norm.get_neighbours_candidates(tweet_pos_tagged,ovv_word,ovv_tag)
                lo_candidates.append({'ovv_word' : ovv_word , 'tag' : ovv_tag , 'cands' : candidates})
    return lo_candidates

def in_suggestions(results,ovv,index_count=False):
    pos = {} if index_count else 0
    neg = 0
    dictinary = enchant.Dict("en_US")
    for tweet in results:
        for word in tweet:
            # word = (u'comming', u'OOV', u'coming')
            if ovv(word[0],word[1]):
                suggestions = [sug for sug in  dictinary.suggest(word[0]) if dictinary.check(sug)]
                if word[2] in suggestions:
                    if index_count:
                        pos[suggestions.index(word[2])] = pos.get(suggestions.index(word[2]),0) + 1
                    else:
                        pos += 1
                else:
                    neg += 1
    print '%s positive result, %d negative result' % (pos, neg)

def metaphone_match(results,ovv):
    pos = 0
    neg = 0
    for tweet in results:
        for word in tweet:
            if ovv(word[0],word[1]):
                met_ovv = set([met for met in set(DMetaphone(4)(word[0])) if met is not None])
                met_cand = [met for met in set(DMetaphone(4)(word[2])) if met is not None]
                intersects =  met_ovv.intersection(met_cand)
                if len(intersects):
                    pos += 1
                else:
                    print '%s [%s] : %s and %s %s' % (word[0],word[2], met_ovv , met_cand ,intersects)
                    neg += 1
    print '%s positive result, %d negative result' % (pos, neg)

def contains(tweets,results,ovv):
    lo_tweets = CMUTweetTagger.runtagger_parse(tweets)
    N = normalizer.Normalizer(lo_tweets,database='tweets');
    pos = 0
    pos_dict = {}
    lo_candidates = []
    neg = 0
    for i in range(0,len(results)):
        tweet = results[i]
        tweet_pos_tags = CMUTweetTagger.runtagger_parse([tweets[i]])[0] # since only 1 tweet
        for j in range(0,len(tweet)):
            word = tweet[j]
            if ovv(word[0],word[1]):
                ovv_word = word[0]
                tag = tweet_pos_tags[j][1]
                candidates = N.normalize(ovv_word.decode(), tag, j, tweet_pos_tags ,allCands=True)
                index = [candidates.index(x) for x in candidates if x[0] == word[2]]
                if index:
                    pos += 1
                    pos_dict[index[0]] = pos_dict.get(index[0],0) + 1
                    print '%s :[%s]%s ' % (word[0],index[0],word[2])
                else:
                    neg += 1
                lo_candidates.append({ovv_word : candidates, 'contains' : True if index else False })
    print '%s positive result, %d negative result' % (pos, neg)
    print pos_dict
    return lo_candidates

def repeat_check(results,ovv):
    pass


def check(results,ovv,method):
    pos = 0
    neg = 0
    for tweet in results:
        for word in tweet:
            if ovv(word[0],word[1]):
                method(results,ovv)

def run(matrix1,feat_mat,slang):
    if not matrix1:
        matrix1 = tools.load_from_file()
    from constants import mapping as mapp
    if not slang:
        slang = tools.get_slangs()
    edit_dis=2
    met_dis=1
    if not feat_mat:
        feat_mat = iter_calc_lev_sndx(matrix1)
        feat_mat = add_slangs(feat_mat,mapp,slang)
    feat_mat1 = copy.deepcopy(feat_mat)
    res = show_results(feat_mat1, mapp,
                       dim=[0.2, 0.2, 0.2, 0.2, 0., 0.2, 1] ,
                       max_val=[1, 1, 1, 1, 0, 1./1739259 , 1])
    index_list,nil,nnnn = tools.top_n(res,verbose=False)
    return feat_mat,res
