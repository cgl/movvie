from scoring import han,pennel
import enchant
from fuzzy import DMetaphone
import normalizer
import CMUTweetTagger
import tools
import numpy
import re
import copy
import traceback
import logging
import constants

is_ill = lambda x,y,z : True if x != z else False
is_ovv = lambda x,y,z : True if y == 'OOV' else False
ovvFunc = is_ill
dic= enchant.Dict("en_US")
slang = tools.get_slangs()
met_map = {}

def detect_ovv(slang):
    from constants import mapping as mapp
    not_ovv= []
    for ind in range (0,len(mapp)):
        ovv = mapp[ind][0]
        ovv_reduced = re.sub(r'(.)\1+', r'\1', ovv).lower()
        if slang.has_key(ovv_reduced):
            sl = slang.get(ovv) or slang.get(ovv_reduced)
            if len(sl.split(" ")) >  1:
                not_ovv.append(ovv)
            else:
                not_ovv.append('')
        elif ovv.isdigit():
            not_ovv.append(ovv)
#        elif len(ovv_reduced) > 1 and dic.check(ovv_reduced.capitalize()):
#            not_ovv.append(ovv_reduced.capitalize())
        elif not ovv_reduced.isalnum():
            not_ovv.append(ovv)
        else:
            not_ovv.append('')
    i = 0
    for ind,words in enumerate(mapp):
        if words[0] == words[1]:
            if not not_ovv[ind]:
                i+=1
    print i," not ovv detected"
    return not_ovv


def add_from_dict(fm,mat,distance,not_ovv = detect_ovv(slang)):
    clean_words = tools.get_clean_words()
    for ind,cands in enumerate(fm):
        if not not_ovv[ind]:
            cands = find_more_results(mat[ind][0][0],mat[ind][0][1],cands,clean_words,distance)
    return fm

def find_more_results(ovv,ovv_tag,cand_dict,clean_words,distance,give_suggestions=True):
    cands = tools.get_from_dict_met(ovv,met_map)
    cands_more = tools.get_from_dict_dis(ovv,ovv_tag,clean_words,distance)
    cands.extend(cands_more)
    cands = list(set(cands))
    if give_suggestions:
        sugs = tools.get_suggestions(ovv,ovv_tag)
        cands.extend(sugs)
    for cand in cands:
        if not cand_dict.has_key(cand):
            cand_dict[cand] = get_score_line(cand,0,ovv,ovv_tag)
    return cand_dict

def iter_calc_lev(matrix,fm,not_ovv = detect_ovv(slang),edit_dis=2,met_dis=1,verbose=False):
    for ind,cands in enumerate(fm):
        if not not_ovv[ind]:
            cands = get_candidates_from_graph(matrix[ind],matrix[ind][0][0], matrix[ind][0][1],cands,edit_dis,met_dis)
    return fm

def get_candidates_from_graph(matrix_line,ovv,ovv_tag,cand_dict,edit_dis,met_dis):
    filtered_cand_list = [cand for cand in matrix_line[1]
                          if cand_dict.has_key(cand) or tools.filter_cand(ovv,cand,edit_dis=edit_dis,met_dis=met_dis)]

    for cand in filtered_cand_list:
        sumof = 0.
        for a,b in matrix_line[2][matrix_line[1].index(cand)]:
            sumof += a[0]/a[1]
        if not cand_dict.has_key(cand):
            cand_dict[cand] = get_score_line(cand,sumof,ovv,ovv_tag)
        else:
            cand_dict[cand][0] = sumof
    return cand_dict

def get_score_line(cand,sumof,ovv,ovv_tag):
    node =  tools.get_node(cand,tag=ovv_tag)
    freq = freq_score(int(node['freq'])) if node else 0.
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

def freq_score(freq):
    if freq >= 715:
        return 1
    elif freq >= 327:
        return 0.8
    elif freq >= 205:
        return 0.6
    elif freq >= 100:
        return 0.4
    elif freq >= 9:
        return 0.2
    else:
        return 0

def add_slangs(mat,slang,verbose=False):
    res_mat = []
    for ind in range (0,len(mat)):
        ovv = mat[ind][0][0]
        ovv_reduced = re.sub(r'(.)\1+', r'\1\1', ovv).lower()
        cands = {}
        if slang.has_key(ovv_reduced):
            sl = slang.get(ovv_reduced).lower()
            if len(sl.split(" ")) <=  1:
                ovv_tag =  mat[ind][0][1]
                res_line = get_score_line(sl,0,ovv,ovv_tag)
                res_line[4] = 1
                cands[sl] = res_line
                if verbose:
                    print ind,ovv,sl,cands[sl]
        res_mat.append(cands)
    return res_mat

def calculate_score(res_vec,max_val):
    try:
        score  =  res_vec[0] * max_val[0]  # weight
        score +=  res_vec[1] * max_val[1]  # lcsr
        score +=  res_vec[2] * max_val[2]  # distance
        score +=  res_vec[3] * max_val[3]  # common letter
        score +=  res_vec[4] * max_val[4]  # slang
        score +=  res_vec[5] * max_val[5]  # freq
        return score
    except IndexError, i:
        print res_vec,i
    except TypeError, e:
        print res_vec
        print traceback.format_exc()

def add_nom_verbs(fm,mapp,slang_threshold=1):
    for ind,cands in enumerate(fm):
        ovv = mapp[ind][0]
        ovv_tag = mapp[ind][2]
        if ovv_tag == "L" :
            if ovv.lower() == u"im":
                cand = u"i'm"
                add_candidate(cands,cand,ovv,ovv_tag,slang_threshold)
        elif ovv_tag == u"~":
            if ovv.lower() == u"cont":
                cand = u'continued'
                add_candidate(cands,cand,ovv,ovv_tag,slang_threshold)
        elif ovv_tag == u"P":
            if tools.pronouns.has_key(ovv):
                cand = tools.pronouns[ovv]
                add_candidate(cands,cand,ovv,ovv_tag,slang_threshold)
        elif ovv_tag == u"R":
            if ovv == u"2":
                cand = u"too"
                add_candidate(cands,cand,ovv,ovv_tag,slang_threshold)
        cand = tools.get_reduced_alt(ovv)
        if cand and ovv != cand:
            add_candidate(cands,cand,ovv,ovv_tag,slang_threshold*0.8)
        cand = tools.replace_digits_alt(ovv)
        if cand and ovv != cand:
            add_candidate(cands,cand,ovv,ovv_tag,slang_threshold)
    return fm

def add_candidate(cands,cand,ovv,ovv_tag,slang_threshold):
    if not cands.has_key(cand):
        cands[cand] = get_score_line(cand,0,ovv,ovv_tag)
    cands[cand][4] = slang_threshold

#--------------------------------------------------------------

def calc_score_matrix(lo_postagged_tweets,ovv_fun,window_size, database='tweets'):
    lo_candidates = []
    norm = normalizer.Normalizer(lo_postagged_tweets,database=database)
    norm.m = window_size/2
    for tweet_ind in range(0,len(lo_postagged_tweets)):
        tweet_pos_tagged = lo_postagged_tweets[tweet_ind]
        for j in range(0,len(tweet_pos_tagged)):
            word = tweet_pos_tagged[j]
            if ovv_fun(word[0],word[1],word[2]):
                ovv_word = word[0]
                ovv_tag = tweet_pos_tagged[j][1]
                keys,score_matrix = norm.get_candidates_scores(tweet_pos_tagged,ovv_word,ovv_tag)
                ovv_word_reduced = re.sub(r'(.)\1+', r'\1\1', ovv_word).lower()
                ovv_word_digited = tools.replace_digits(ovv_word_reduced)
                lo_candidates.append([(ovv_word_digited,ovv_tag),keys,score_matrix])
#            elif word[1] == "OOV":
#                lo_candidates.append([(word[0],ovv_tag),[word[0]],
#                                      [[[numpy.array([ 9.93355, 4191.]), 'new|A'],
#                                        [numpy.array([ 1.26120, 4.1910]), 'pix|N']]]])
    return lo_candidates

def construct_mapp(pos_tagged,oov_fun):
    mapp = []
    for t_ind,tweet in enumerate(pos_tagged):
        for w_ind,(word,stag,cor) in enumerate(tweet):
            if oov_fun(word,stag,cor):
                mapp.append((word,cor,pos_tagged[t_ind][w_ind][1]))
    return mapp

def test_detection(index,oov_fun):
    pos_tagged = constants.pos_tagged[index:index+1]
    results = constants.results[index:index+1]
    matrix1 = calc_score_matrix(pos_tagged,oov_fun,7,database='tweets2')
    mapp = construct_mapp(pos_tagged, oov_fun)
    all_oov =  ['' for word in pos_tagged ]
    print(pos_tagged)
    set_oov_detect = run(matrix1,[],[],slang,all_oov,mapp)
    for found in set_oov_detect[0]:
        if found and len(found[0]) > 0:
            print(found[0][0])
    return set_oov_detect

def calc_results(res_mat,not_ovv, max_val = [1., 1., 0.5, 0.0, 1.0, 0.5], threshold = 1.5):
    results = []
    for ind in range (0,len(res_mat)):
        if not_ovv and not_ovv[ind]:
            res_list = [[not_ovv[ind],0,0,0,0,0,0]]
        else:
            res_dict = copy.deepcopy(res_mat[ind])
            res_list = []
            if res_dict:
                for cand in res_dict:
                    score = calculate_score(res_dict[cand],max_val)
                    if score >= threshold:
                        res_dict[cand].append(round(score,7))
                        res_line = [cand]
                        res_line.extend(res_dict[cand])
                        res_list.append(res_line)
                res_list.sort(key=lambda x: -float(x[-1]))
        results.append(res_list)
    return results

def run(tweets, slang, not_oov, threshold=1.5, slang_threshold=1,
        max_val = [1., 1., 0.5, 0.0, 1.0, 0.5], distance = 2, oov_fun = ovvFunc):
    pos_tagged = CMUTweetTagger.runtagger_parse(tweets)
    window_size = 7
    matrix1 = calc_score_matrix(pos_tagged, oov_fun, window_size,database='tweets2')
    if not slang:
        slang = tools.get_slangs()
    fms = add_slangs(matrix1,slang)
    fmd = add_from_dict(fms, matrix1, distance, not_oov)
    mapp = construct_mapp(pos_tagged,oov_fun)
    fm_reduced = add_nom_verbs(fmd,mapp ,slang_threshold=slang_threshold)
    feat_mat = iter_calc_lev(matrix1,fm_reduced, not_ovv = not_oov)
    res = calc_results(feat_mat, not_oov, max_val = max_val, threshold = threshold)
    return res
