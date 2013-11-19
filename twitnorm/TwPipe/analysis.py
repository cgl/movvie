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

tweets,results = han(548)
ovvFunc = lambda x,y : True if y == 'OOV' else False
dic= enchant.Dict("en_US")
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
        scores.append(get_score_line(cand,0,ovv,ovv_tag,None,None)[0])
    return scores

def calc_lev_sndx(mat,ind,edit_dis=2,met_dis=1,verbose=True):
    result_list = []
    matrix = mat[ind]
    ovv = matrix[0].encode('utf-8')
    ovv_tag = tools.get_tag(ind,ovv)
    ovv_snd = soundex.soundex(ovv)
    length = len(matrix[1])
    suggestions = tools.get_suggestions(ovv,ovv_tag)
    suggestions_found = []
    if verbose:
        print '%s: found %d candidate' %(ovv,length)
    for cand in [cand for cand in matrix[1]
                 if tools.filter_cand(ovv,cand,edit_dis=edit_dis,met_dis=met_dis)]:
        sumof = 0.
        for a,b in matrix[2][matrix[1].index(cand)]:
            sumof += a[0]/a[1]
        line, in_sugs = get_score_line(cand,sumof,ovv,ovv_tag,ovv_snd,suggestions)
        if in_sugs:
            suggestions_found.append(cand)
        result_list.append(line)
    if not result_list:
        result_list = find_more_results(ovv,ovv_tag)
    result_list.extend([get_score_line(sug, 0. ,ovv,ovv_tag, ovv_snd, suggestions)[0]
                        for sug in suggestions[:15]
                        if sug not in suggestions_found
                        and
                        tools.filter_cand(ovv,sug) ])
    #    print ovv,suggestions
    result_list.sort(key=lambda x: -float(x[1]))
    return result_list

def get_score_line(cand,sumof,ovv,ovv_tag, ovv_snd,suggestions):
    if suggestions and cand in suggestions:
        suggestion_score = 1./(1.+suggestions.index(cand))
        found = True
    else:
        suggestion_score = 0.
        found = False

    node =  tools.get_node(cand,tag=ovv_tag)
    freq = node['freq'] if node else 0.
    line = [cand,
            sumof,                                # weight
            tools.lcsr(ovv,cand),                 # lcsr
            tools.distance(ovv,cand),             # distance
            tools.common_letter_score(ovv,cand),  # shared letter
            suggestion_score ,
            freq,
    ]
    for ind in range(1,len(line)):
        line[ind] = round(line[ind],8)
    return line , found

def iter_calc_lev_sndx(mat,edit_dis=2,met_dis=1,verbose=False):
    mat_scored = []
    for ind in range (0,len(mat)):
        res_list = calc_lev_sndx(mat,ind,verbose=verbose)
        mat_scored.append(res_list)
    return mat_scored

def show_results(res_mat,mapp, dim = [ 0.2, 0.2, 0.2, 0.2 , 0.1, 0.2], max_val = [1,1,1,1,0,1/1739259.0], verbose=True):
    results = []
    pos = 0
    for ind in range (0,len(res_mat)):
        correct = False
        #max_val = [ 0.9472,  1.        ,  1.        ,  1.      , 1. , 0.86099657]
        #[0.503476, 1.0, 1.0, 1.0, 146234.0,]
        res_list = res_mat[ind]
        if res_list:
            for res_ind in range (0,len(res_list)):
                score = calculate_score(res_list[res_ind],dim,max_val)
                res_list[res_ind].append(round(score,7))
            res_list.sort(key=lambda x: -float(x[-1]))
            if res_list[0][0] == mapp[ind][1]:
                correct = True
                pos += 1
            if verbose:
                print '%s : %s [%s]' % ('Found' if correct else '', res_list[ind][0],mapp[ind][1])
        results.append(res_list)
    print 'Number of correct answers %s' % pos
    return results


def calculate_score(res_vec,dim,max_val):
    try:
        score  = dim[0] * res_vec[1] * max_val[0]  # weight
        score += dim[1] * res_vec[2] * max_val[1]  # lcsr
        score += dim[2] * res_vec[3] * max_val[2]  # distance
        score += dim[3] * res_vec[4] * max_val[3]  # common letter
        score += dim[4] * res_vec[5] * max_val[4]  # suggestion score
        score += dim[5] * res_vec[6] * max_val[5]  # freq

        return score
    except IndexError, i:
        print res_vec,i

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
