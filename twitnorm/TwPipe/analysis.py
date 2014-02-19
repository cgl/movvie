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
OOVFUNC = is_ill
SLANG = tools.get_slangs()

# create file handler which logs even debug messages
fh = logging.FileHandler('analysis.log')
fh.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

fh.setFormatter(formatter)
# add the handlers to logger
root_logger = logging.getLogger()
root_logger.propagate = False
root_logger.addHandler(fh)
#root_logger.disabled = True

def main(index=False):
    results = han(549)[1]
    ovv = lambda x,y : True if y == 'OOV' else False
    in_suggestions(results,ovv,index_count=index)

if __name__ == "__main__ ":
    main()

# Bu fonksiyon ne is yapiyor belli degil
def detect_ovv(slang,mapp):
    not_ovv = []
    for ind in range (0,len(mapp)):
        ovv = mapp[ind][0]
        ovv_reduced = tools.get_reduced_alt(ovv) or ovv
        if slang.has_key(ovv_reduced):
            s_word = slang.get(ovv) or slang.get(ovv_reduced)
            if len(s_word.split(" ")) >  1:
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
                i += 1
    print i," not ovv detected"
    return not_ovv


def add_from_dict(fm, mat, distance, not_ovv):
    clean_words = tools.get_clean_words()
    for ind,cands in enumerate(fm):
        if not not_ovv[ind]:
            cands = find_more_results(mat[ind][0][0],mat[ind][0][1],cands,clean_words,distance)
    return fm

def find_more_results(ovv,ovv_tag,cand_dict,clean_words,distance,give_suggestions=True):
    cands = tools.get_from_dict_met(ovv,{})
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

def iter_calc_lev(matrix, fm, not_ovv ,edit_dis=2,met_dis=1,verbose=False):
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
        ovv_reduced = tools.get_reduced_alt(ovv) or ovv
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

# tweets, results = han(548)
def calc_each_neighbours_score(tweets_str, results, ovv,tweets):
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
    for tweet in results:
        for word in tweet:
            if ovv(word[0],word[1]):
                method(results,ovv)

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

def calc_score_matrix(lo_postagged_tweets,results,ovv_fun,window_size, database='tweets'):
    lo_candidates = []
    norm = normalizer.Normalizer(lo_postagged_tweets,database=database)
    norm.m = window_size/2
    for tweet_ind in range(0,len(lo_postagged_tweets)):
        tweet_pos_tagged = lo_postagged_tweets[tweet_ind]
        for j in range(0,len(tweet_pos_tagged)):
            word = results[tweet_ind][j]
            if ovv_fun(word[0],word[1],word[2]):
                ovv_word = word[0]
                ovv_tag = tweet_pos_tagged[j][1]
                keys,score_matrix = norm.get_candidates_scores(tweet_pos_tagged,ovv_word,ovv_tag)
                ovv_word_reduced = tools.get_reduced_alt(ovv_word) or ovv_word
                ovv_word_digited = tools.replace_digits(ovv_word_reduced)
                lo_candidates.append([(ovv_word_digited,ovv_tag),keys,score_matrix])
            #elif word[1] == "OOV":
            #    lo_candidates.append([(word[0],ovv_tag),[word[0]],
            #                          [[[numpy.array([    9.93355,  4191.     ]), 'new|A'],
            #                            [numpy.array([  1.26120000e+00,   4.19100000e+03]), 'pix|N']]]
            #                      ])
    return lo_candidates


    '''
            if trans.__class__ == str:
                ovv_word = ovv_word.replace(m.group(0),trans)
            else:
                transes = [ovv_word.replace(m.group(0),t) for t in trans]
                transes_scored = [(t,tools.get_node(t)[0]['freq'] if tools.get_node(t) else 0) for (t in transes]
                transes_scored.sort(key=lambda x: x[1])
                ovv_word = transes_scored[-1][0]
    '''

def construct_mapp_penn(pos_tagged_penn, results_penn):
    mapp_penn = []
    for t_ind,tweet in enumerate(results_penn):
        for w_ind,(word,stag,cor) in enumerate(tweet):
            if stag == "OOV":
                mapp_penn.append((word,cor,pos_tagged_penn[t_ind][w_ind][1]))
    return mapp_penn

def calculate_score_penn(hyp_file,ref_file, ovv_fun = OOVFUNC, threshold=1.5):
    tweets_penn,results_penn = pennel(5000,hyp_file,ref_file)
    pos_tagged_penn = CMUTweetTagger.runtagger_parse(tweets_penn)
    window_size = 5
    matrix_penn = calc_score_matrix(pos_tagged_penn, results_penn, ovv_fun, window_size, database='tweets2')
    mapp_penn = construct_mapp_penn(pos_tagged_penn, results_penn)
    bos_ovv_penn = ['' for word in mapp_penn ]
    set_penn = run(matrix_penn,[],[],bos_ovv_penn,results = results_penn, pos_tagged = pos_tagged_penn,oov_fun = ovv_fun, threshold=threshold)
    return set_penn, mapp_penn, results_penn, pos_tagged_penn

def construct_mapp(pos_tagged, results,oov_fun):
    mapp = []
    for t_ind,tweet in enumerate(results):
        for w_ind,(word,stag,cor) in enumerate(tweet):
            if oov_fun(word,stag,cor):
                mapp.append((word,cor,pos_tagged[t_ind][w_ind][1]))
    return mapp

def test_detection(index,oov_fun):
    if index:
        pos_tagged = constants.pos_tagged[index:index+1]
        results = constants.results[index:index+1]
    else:
        pos_tagged = constants.pos_tagged
        results = constants.results
    matrix1 = calc_score_matrix(pos_tagged,results,oov_fun,7,database='tweets2')
    mapp = construct_mapp(pos_tagged, results, oov_fun)
    all_oov =  ['' for word in mapp ]
    set_oov_detect = run(matrix1,[],[],all_oov,results = results, pos_tagged = pos_tagged, oov_fun = oov_fun)
    return set_oov_detect

def show_results(res_mat,mapp, not_ovv = [], max_val = [1., 1., 0.5, 0.0, 1.0, 0.5], verbose = False, threshold = 1.5):
    results = []
    correct_answers = [] # True Positive
    incorrect_answers = [] # False Negative
    miss = []
    total_pos = 0
    incorrectly_corrected_word = 0 # False Positive
    correctly_unchanged = [] # True Negative
    for ind in range (0,len(res_mat)):
        correct = False
        ovv = mapp[ind][0]
        if not_ovv and not_ovv[ind]:
            res_list = [[not_ovv[ind],0,0,0,0,0,0]]
        else:
            res_dict = copy.deepcopy(res_mat[ind])
            res_list = []
            if res_dict:
                for res_ind,cand in enumerate(res_dict):
                    score = calculate_score(res_dict[cand],max_val)
                    if score >= threshold:
                        res_dict[cand].append(round(score,7))
                        res_line = [cand]
                        res_line.extend(res_dict[cand])
                        res_list.append(res_line)
                res_list.sort(key=lambda x: -float(x[-1]))
        answer = res_list[0][0] if res_list else ovv
        correct_answer = mapp[ind][1]
        if answer.lower() == correct_answer.lower():
            total_pos += 1
        if answer != ovv: # ppl --> people , people --> ppl, ppl --> apple
            if answer.lower() == correct_answer.lower() : # tp: ppl --> people
                correct = True
                correct_answers.append((ind,answer))
            else:
                if ovv == correct_answer: # fp: people --> ppl
                    incorrectly_corrected_word += 1
                else:                     # fn: ppl --> apple
                    incorrect_answers.append((ind,answer))
        else: # people --> people , ppl --> ppl
            if ovv != correct_answer: # fn: ppl  --> ppl
                incorrect_answers.append((ind,answer))
            else:                     # tn: people --> people
                correctly_unchanged.append((ind,answer))
        if verbose:
            print '%d. %s | %s [%s] :%s' % (ind, 'Found' if correct else '', mapp[ind][0],mapp[ind][1],res_list[0][0])
        results.append(res_list)
    print 'Number of correct normalizations %s, incorrect normalizations %s, changed correct token %s, total correct token ratio %s/%s' % (
        len(correct_answers),len(incorrect_answers),incorrectly_corrected_word,total_pos,len(mapp))
    return results,correct_answers,incorrect_answers, incorrectly_corrected_word, correctly_unchanged

def calc_mat(results = constants.results, pos_tagged = constants.pos_tagged, oov_fun = OOVFUNC):
    window_size = 7
    matrix = calc_score_matrix(pos_tagged,results,oov_fun,window_size,database='tweets2')
    return matrix

def run(matrix1,fmd,feat_mat,not_ovv,results = constants.results,
        pos_tagged = constants.pos_tagged, threshold=1.5,slang_threshold=1,
        max_val = [1., 1., 0.5, 0.0, 1.0, 0.5], verbose=False, distance = 2,
        oov_fun = OOVFUNC):
    mapp = construct_mapp(pos_tagged, results, oov_fun)
    if not matrix1:
        matrix1 = calc_mat(results = results, pos_tagged = pos_tagged, oov_fun = oov_fun)
    #max_val=[1.0, 1.0, 1.0, 1.0, 5.0, 1./1873142]
    fms = add_slangs(matrix1,SLANG)
    if not fmd:
        fmd = add_from_dict(fms,matrix1,distance,not_ovv)
    fm_reduced = add_nom_verbs(fmd,mapp,slang_threshold=slang_threshold)
    if not feat_mat:
        feat_mat = iter_calc_lev(matrix1,fm_reduced,mapp,not_ovv)
        #feat_mat2 = add_weight(feat_mat,mapp,not_ovv)
    res,ans,incor, fp, tn = show_results(feat_mat, mapp, not_ovv = not_ovv, max_val=max_val,threshold=threshold)
    try:
        ann_and_pos_tag = tools.build_mappings(results,pos_tagged,oov_fun)
        index_list,nil,no_res = tools.top_n(res,not_ovv,mapp,ann_and_pos_tag,verbose=verbose)
        num_of_normed_words = len(ans) + len(incor)
        num_of_words_req_norm = len(filter(lambda x: x[0] != x[1], mapp))
        tools.get_performance(len(ans),len(incor),fp)
        threshold = tools.get_score_threshold(index_list,res)
        tools.test_threshold(res,threshold)
        return [res, feat_mat, fmd, matrix1, ans, incor, nil, no_res, index_list, mapp, tn]
        #        0   1         2    3        4    5      6    7       8           9     10
    except:
        print(traceback.format_exc())
        return [res, feat_mat, fmd, matrix1, ans, incor]
