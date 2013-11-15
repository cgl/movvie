from scoring import han
import enchant
from fuzzy import DMetaphone
import normalizer
import soundex
import Levenshtein
import CMUTweetTagger
import enchant
import tools

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


def calc_lev_sndx(mat,ind,verbose=True):
    result_list = []
    matrix = mat[ind]
    ovv = matrix[0].encode('utf-8')
    ovv_snd = soundex.soundex(ovv)
    length = len(matrix[1])
    suggestions = [word for word in dic.suggest(ovv)
                   if dic.check(word) and len(word)>2 and tools.get_node(word.decode("utf-8","ignore"))]
    suggestions_found = []
    if verbose:
        print '%s: found %d candidate' %(ovv,length)
    for cand in [cand for cand in matrix[1]
                 if Levenshtein.distance(ovv_snd,soundex.soundex(cand.encode('utf-8'))) < 2]:
        sumof = 0
        for a,b in matrix[2][matrix[1].index(cand)]:
            sumof += a[0]/a[1]
        line, in_suggestions = get_score_line(cand,sumof,ovv_snd,ovv,suggestions)
        if in_suggestions:
            suggestions_found.append(cand)
        result_list.append(line)
    result_list.extend([get_score_line(sug, 0,ovv, ovv_snd, suggestions)
                        for sug in suggestions[:10]
                        if sug not in suggestions_found
                        and
                        Levenshtein.distance(ovv_snd,soundex.soundex(sug)) < 2 ])
#    print ovv,suggestions
    result_list.sort(key=lambda x: -float(x[1]))
    return result_list

def get_score_line(cand,sumof,ovv,ovv_snd,suggestions):
    if cand in suggestions:
        suggestion_score = 1./(1.+suggestions.index(cand))
        found = True
    else:
        suggestion_score = 0
        found = False
    return [cand, sumof,
                Levenshtein.distance(ovv_snd,soundex.soundex(cand.decode("utf-8","ignore"))),
                float(len(set(ovv).intersection(set(cand)))) / float(len(set(ovv).union(set(cand)))),
                suggestion_score ], found

def iter_calc_lev_sndx(mat,verbose=False):
    mat_scored = []
    for ind in range (0,len(mat)):
        res_list = calc_lev_sndx(mat,ind,verbose=verbose)
        mat_scored.append(res_list)
    return mat_scored

def show_results(res_mat,mapp, d1 = 0.3, d2 = 0.1, d3 = 0.3, d4 = 0.3 ,verbose=True):
    results = []
    pos = 0
    for ind in range (0,len(res_mat)):
        correct = False
        max_val = [  0.59405118,   1.        ,   1.        ,  13.]
        if res_mat:
            for res_ind in range (0,len(res_mat)):
                res_mat[res_ind].append(
                    d1 * (res_mat[res_ind][1]/max_val[0]) + (d2 *(1 - res_mat[res_ind][2])) +
                    d3 * res_mat[res_ind][3] + d4 * (res_mat[res_ind][4]/max_val[3]))
            res_mat.sort(key=lambda x: -float(x[-1]))
            if res_mat[0][0] == mapp[ind][1]:
                correct = True
                pos += 1
            if verbose:
                print '%s : %s [%s]' % ('Found' if correct else '', res_mat[ind][0],mapp[ind][1])
        results.append(res_mat)
    print 'Number of correct answers %s' % pos
    return results


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
