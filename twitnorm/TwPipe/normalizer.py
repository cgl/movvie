import enchant
from pymongo import MongoClient
from tools import isMention, isHashtag, isvalid
import Levenshtein as Lev
import fuzzy
from math import log


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
        ovvTag = tag
        ovvInd = word_ind
        scores = {}
        scores = self.returnCandRight(tweet,ovvWord,ovvInd, ovvTag,{})
        scores = self.returnCandLeft(tweet,ovvWord,ovvInd, ovvTag,scores)
        for sug in filter(self.d.check,self.d.suggest(ovvWord)):
            self.updateScore(scores,sug,len(ovvWord)/(Lev.distance(ovvWord,sug)+0.000001))
        scores_sorted = sorted(scores.items(), key= lambda x: x[1], reverse=True)
        if scores_sorted:
            #print 'Ovv: "%s" with tag: %s corrected as: "%s" with a score %d' %(ovvWord,ovvTag, scores_sorted[0][0], scores_sorted[0][1])
            if allCands:
                return scores_sorted
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
#        print 'Ovv: %s with tag %s' %(ovvWord,ovvTag)
        neighbours = tweet[ovvInd-self.m:ovvInd]
        for ind2,n in enumerate(neighbours):
            neighNode = n[0].strip()+'|'+n[1]
            # For each word next to ovv we look to the graph for candidates thatshares same distance and tag with the ovv
            distance = len(neighbours)-ind2
            # find all the non ovv nodes from the neighbour with same dis
            candidates_q = self.edges.find({'from':neighNode, 'to_tag': ovvTag, 'dis': { '$in' : [distance, (distance - 1)] }, 'weight' : { '$gt': 1 } })

            # filter candidates who has a different tag than ovv
            cands_q = [{'to':node['to'], 'weight':node['weight']/self.nodes.find_one({'_id':node['to'],'tag': ovvTag, 'ovv':False })['freq']} for node in candidates_q ]
            # filter(lambda x: self.nodes.find_one({'_id':x['to'],'tag': ovvTag, 'ovv':False }), candidates_q)
            n = distance
            scores = self.score(ovvWord,cands_q,n,scores)
        return scores

    def returnCandLeft(self,tweet,ovvWord,ovvInd, ovvTag,scores):
#        print 'Ovv: %s with tag %s' %(ovvWord,ovvTag)
        neighbours = tweet[ovvInd+1:ovvInd+1+self.m]
        for ind2,n in enumerate(neighbours):
            neighNode = n[0].strip()+'|'+n[1]
            # For each word next to ovv we look to the graph for candidates thatshares same distance and tag with the ovv
            distance = ind2
            # find all the non ovv nodes from the neighbour with same dis
            candidates_q = self.edges.find({'to':neighNode, 'from_tag': ovvTag ,'dis': { '$in' : [distance, (distance - 1)] }, 'weight' : { '$gt': 1 } })

            # filter candidates who has a different tag than ovv
            cands_q =  [{'to':node['to'], 'weight':node['weight']/self.nodes.find_one({'_id':node['from'],'tag': ovvTag, 'ovv':False })['freq']} for node in candidates_q ]  #= filter(lambda x: self.nodes.find_one({'_id':x['from'],'tag': ovvTag, 'ovv':False }), candidates_q)
            n = distance
            scores = self.score(ovvWord,cands_q,n,scores)
        return scores

    def score(self, ovvWord, cands_q, n, scores):
        metOvv = set(fuzzy.DMetaphone(4)(ovvWord))
        for cand_q in cands_q:
            cand = cand_q['to'].split('|')[0]
            try:
                lev = Lev.distance(str(ovvWord), str(cand)) + 0.000001
            except UnicodeEncodeError:
                lev = len(ovvWord)
                print 'UnicodeEncodeError: %s' % ovvWord
            met = len(metOvv.intersection(fuzzy.DMetaphone(4)(cand))) or 0.000001
            score = (4-n)*log(cand_q['weight'])/ lev * met
            self.updateScore(scores,cand,score)
        return scores


    def updateScore(self,scores,cand,score):
        if scores.has_key(cand):
            score += scores.get(cand)
            scores.update({cand:score})
        else:
            scores[cand] = score
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
