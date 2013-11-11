import enchant
from pymongo import MongoClient
from tools import isMention, isHashtag, isvalid
import Levenshtein as Lev
import fuzzy
from math import log
from  numpy import array
import pdb


salient=0.00000000001
class Normalizer:

    # input is a list s.t.
#lot = [[('example', 'N', 0.979), ('tweet', 'V', 0.7763), ('1', '$', 0.9916)],
#       [('example', 'N', 0.979), ('tweet', 'V', 0.7713), ('2', '$', 0.5832)]]
    def __init__(self, input, database='tweets',method='normalize'):
        n = 4  # n-gram
        self.method = method
        self.m = n - 1
        self.texts = input
        self.d = enchant.Dict("en_US")
        client = MongoClient('localhost', 27017)
        db = client[database]
        self.nodes = db['nodes']
        self.edges = db['edges']
        self.ovvLists = [[ind for ind, t in enumerate(text)
                          if self.isOvv(t[0], t[1])] for text in self.texts]
    def isOvvStr(self, w, t):
        return 'OVV' if self.isOvv(w, t) else 'IV'

    def isOvv(self, w, t):
#            if not isvalid(w):
        if t in [',','E','~','@','U']: # punctuation, emoticon, discourse marker, mention, url
            return False
        elif t in ['$',] or isMention(w): # Numeral or url or mention
            return False
        elif t in ['#'] or isHashtag(w):
            return False
        elif not isvalid(w) and t is not '&' :
            #print '%s : %s is not ovv' % (t, w)
            return False
        else:
            return not self.d.check(w)


    def normalizeAll(self):
        results = []
        for ind,tweet in enumerate(self.texts):
            tweet_result = [ self.make_tuple(word.decode(),tag,word_ind,ind) for (word_ind ,(word, tag, conf)) in enumerate(tweet)]
            results.append(tweet_result)
        return results

    # Given a word and its pos tag normalizes it IF NECESSARY
    # Given also the whole tweet and word's index within the tweet
    def normalize(self,word, tag, word_ind, tweet,allCands=False):
#        if self.norm_tricks(word,tag):
#            return self.norm_tricks(word,tag)
#        if not self.isOvv(word,tag):
#            return word
        ovvWord = word
        print ovvWord
        ovvTag = tag
        ovvInd = word_ind
        scores = {}
        scores = self.returnCandRight(tweet,ovvWord,ovvInd, ovvTag,{})
        scores = self.returnCandLeft(tweet,ovvWord,ovvInd, ovvTag,scores)
#        for sug in filter(self.d.check,self.d.suggest(ovvWord)):
#            self.updateScore_suggested(scores,sug,ovvWord,ovvTag)
        scores_sorted = sorted(scores.items(), key= lambda x: x[1][0], reverse=True)
        if scores_sorted:
            #print 'Ovv: "%s" with tag: %s corrected as: "%s" with a score %d' %(ovvWord,ovvTag, scores_sorted[0][0], scores_sorted[0][1])
            if allCands:
                return scores_sorted[:200]
            return scores_sorted[0][0].lower()
        else:
            return word


    def normalize_spell_suggest(self,word, tag, word_ind, tweet):
        if self.d.check(word):
            return word
        suggestions =self.d.suggest(word)
        if not suggestions:
            print word
        else:
            print '%s:  %s' %(word,suggestions[0])
        return suggestions[0].lower() if suggestions and self.d.check(suggestions[0]) else word

    def normalize_return_word(self,word, tag, word_ind, tweet):
        return word

    def make_tuple(self, word, tag, word_ind, tweet_ind):
        normalizer = getattr(self, self.method)
        return (word, self.isOvvStr(word, tag),
                normalizer(word, tag, word_ind, self.texts[tweet_ind]))

    def normAll(self):
        normLists = []
        for ind,tweet in enumerate(self.texts): #ind indicates the tweet id
            if not self.ovvLists[ind]:
                continue
            normLists.append(self.norm(tweet,self.ovvLists[ind]))

        for i,l  in enumerate(self.ovvLists):
            for j,b in enumerate(l):
                print self.texts[i][b]
                print normLists[i][j]
            print '-'

    def norm(self,tweet,ovvList):
        normList = []
        # ovvList is a list of numbers that indicates the index of the ovv word in the tweet
        for ovvInd in ovvList:
            ovvTag = tweet[ovvInd][1]
            ovv = tweet[ovvInd][0]
            #first we get the words that forms an ngram with the ovv
            candidates = filter(self.d.check , self.d.suggest(ovv))
            candidates.append(self.returnCandRight(tweet,ovvInd,ovvTag) or 'A')
            normList.append(candidates[0])
        return normList

    def returnCandRight(self,tweet,ovvWord,ovvInd, ovvTag,scores):
#        pdb.set_trace()
        neigh_start_ind = max(ovvInd-self.m,0)
        neigh_end_ind = ovvInd
        left = False
        position = 'to'
        neigh_position = 'from'
        return self.returnCand(tweet,ovvWord,ovvInd, ovvTag,scores,
                   neigh_start_ind,neigh_end_ind, left, position,neigh_position)

    def returnCandLeft(self,tweet,ovvWord,ovvInd, ovvTag,scores):
#        pdb.set_trace()
        neigh_start_ind = ovvInd+1
        neigh_end_ind = ovvInd+1+self.m
        left = True
        position = 'from'
        neigh_position = 'to'
        return self.returnCand(tweet,ovvWord,ovvInd, ovvTag,scores,
                   neigh_start_ind,neigh_end_ind, left, position,neigh_position)

    def get_neighbours(self,tweet_pos_tagged,ovv):
        froms = []
        tos = []
        for ind,(word, tag, acc) in enumerate(tweet_pos_tagged):
            if word == ovv:
                froms = tweet_pos_tagged[max(ind-self.m,0):ind]
                tos = tweet_pos_tagged[ind+1:ind+1+self.m]
        return froms, tos

    def get_neighbours_candidates(self, tweet_pos_tagged,ovv,ovv_tag):
        froms,tos= self.get_neighbours(tweet_pos_tagged,ovv)
        candidates = []
        for ind,(word, tag, acc) in enumerate(froms):
            neigh_node = word.strip()+'|'+tag
            distance = len(froms) - ind
            cands_q = self.get_cands_with_weigh_freq(ovv , ovv_tag, 'to', 'from', neigh_node , distance )
            candidates.append({'neighbour' : neigh_node, 'tag' : tag, 'cands': cands_q})
        for ind,(word, tag, acc) in enumerate(tos):
            neigh_node = word.strip()+'|'+tag
            distance = ind
            cands_q = self.get_cands_with_weigh_freq(ovv , ovv_tag, 'from', 'to', neigh_node , distance )
            candidates.append({'neighbour' : neigh_node, 'tag' : tag, 'neighbours_cands': cands_q})
        return candidates

    def get_candidates_scores(self, tweet_pos_tagged,ovv,ovv_tag):
        froms,tos= self.get_neighbours(tweet_pos_tagged,ovv)
        keys = []
        score_matrix = []
        for ind,(word, tag, acc) in enumerate(froms):
            neigh_node = word.strip()+'|'+tag
            distance = len(froms) - ind
            cands_q = self.get_cands_with_weigh_freq(ovv , ovv_tag, 'to', 'from', neigh_node , distance )
            keys,score_matrix = self.write_scores(cands_q, keys, score_matrix)
        for ind,(word, tag, acc) in enumerate(tos):
            neigh_node = word.strip()+'|'+tag
            distance = ind
            cands_q = self.get_cands_with_weigh_freq(ovv , ovv_tag, 'from', 'to', neigh_node , distance )
            keys,score_matrix = self.write_scores(cands_q,keys,score_matrix)
        return keys,score_matrix

    @staticmethod
    def write_scores(cands_q,keys,score_matrix):
        for cand_q in cands_q:
            new_scores = array([cand_q['weight']/cand_q['freq'],cand_q['lev'],cand_q['met']])
            if cand_q['to']  not in keys:
                keys.append(cand_q['to'])
                score_matrix.append(new_scores)
            else:
                index = keys.index(cand_q['to'])
                score_matrix[index][0] = score_matrix[index][0] + cand_q['weight']/cand_q['freq']
        return keys,score_matrix

    def returnCand(self,tweet,ovvWord, ovvInd, ovvTag,scores,
                   neigh_start_ind,neigh_end_ind, left, position,neigh_position):
#        print 'Ovv: %s with tag %s' %(ovvWord,ovvTag)
        neighbours = tweet[neigh_start_ind:neigh_end_ind]
        for ind_neigh,neighbour in enumerate(neighbours):
            distance = ind_neigh if left else len(neighbours) - ind_neigh
            neigh_node = neighbour[0].strip()+'|'+neighbour[1]
            # For each word next to ovv we look to the graph for candidates
            # thatshares same distance and tag with the ovv
            # find all the non ovv nodes from the neighbour with same dis
            cands_q = self.get_cands_with_weigh_freq(ovvWord, ovvTag, position, neigh_position, neigh_node,distance)
            n_ind = distance
            scores = self.score(ovvWord,cands_q,n_ind,scores)
        return scores

    def get_cands_with_weigh_freq(self, ovv_word, ovv_tag, position, neigh_position, neigh_node, distance):
        candidates_q = self.edges.find({neigh_position:neigh_node, position+'_tag': ovv_tag,
#                                            'dis': { '$in' : [distance, (distance - 1)] },
                                            'dis': distance ,
                                            'weight' : { '$gt': 1 } })
        if candidates_q.count() < 1 :
            return []
        # filter candidates who has a different tag than ovv
        cands_q = []
        for node in candidates_q:
            node_wo_tag = node[position].split('|')[0]
            if len(node_wo_tag) < 2:
                continue
            to_node = self.nodes.find_one({'_id':node['from'],'tag': ovv_tag, 'ovv':False })
            if(to_node):
                cands_q.append({'position': position, 'to':node_wo_tag, 'weight': node['weight'] , 'freq' : to_node['freq'],
                                'lev': lev_score(ovv_word,node_wo_tag) , 'met': metaphone_score(ovv_word,node_wo_tag)})
        return cands_q

    def score(self, ovvWord, cands_q, n, scores):
        for cand_q in cands_q:
            cand = cand_q['to']
            lev = cands_q['lev']
            met = cands_q['met']
            #self.updateScore(scores,cand,score)
            print '%s: %f %f %f %f' %(cand, cand_q['weight'],cand_q['freq'],lev,met)
            self.updateScore(scores,cand,
                             cand_q['weight'] , lev , met , cand_q['freq'])
        return scores
        #scores_sorted = sorted(scores.items(), key= lambda x: x[1], reverse=True)

    def updateScore_suggested(self,scores,cand,ovv,tag):
        met_set_ovv = set(fuzzy.DMetaphone(4)(ovv))
        met =  metaphone_score(met_set_ovv,cand)
        lev = Lev.distance(ovv,cand) + salient
        node = self.nodes.find_one({'_id':ovv,'tag': tag, 'ovv':False })
        freq = node['freq'] if node else 1
        weight = freq
        freq = 1

        self.updateScore(scores,cand,weight,lev,met,freq)

    def updateScore(self,scores,cand,weight,lev,met,freq):
        #score = log(weight) * (1/lev) * met * log(freq)
        if scores.has_key(cand):
            score_set = scores.get(cand)
        else:
            score_set = array([0,0,0,0,0])
        current_score_set = array([0,weight , (1/lev) , met , freq])
        current_score_set[0] = current_score_set[1:4].prod()
#        print current_score_set[0]
        score_set = current_score_set + score_set
        scores.update({cand:score_set})
        return scores

    def norm_tricks(self,word,tag):
        if word == 'u' and tag == 'O':
            return 'you'
        elif word == 'w' and tag == 'P':
            return 'with'
        elif word == 'lol':
            return 'lol'
        else:
            return None

#UnicodeEncodeError: 'ascii' codec can't encode character u'\xe9' in position 3: ordinal not in range(128) ppl

def metaphone_score(ovv_word,word):
    sim = met_set(ovv_word,word)
    score = 0
    for s in sim:
        if s:
            score += 1
#    print max(score, salient)
    return max(score, salient)
def met_set(ovv_word,word):
    met_s = set(fuzzy.DMetaphone(4)(ovv_word))
    try:
        sim = met_s.intersection(fuzzy.DMetaphone(4)(word))
    except UnicodeEncodeError:
        sim = met_s.intersection(fuzzy.DMetaphone(4)(word.encode('ascii', 'ignore')))
        print 'UnicodeEncodeError[met]: %s %s' % (met_set, word.encode('utf-8'))
    return sim

def lev_score(ovv_word,cand):
    try:
        return Lev.distance(ovv_word, cand) + salient
    except UnicodeEncodeError:
        print 'UnicodeEncodeError[lev]: %s' % ovv_word
        return Lev.distance(ovv_word.encode('ascii', 'ignore'), cand.encode('ascii', 'ignore')) + salient
