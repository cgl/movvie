from graphlib import MTweet
import enchant
from pymongo import MongoClient

class Normalizer:
    # input is a list s.t.
#lot = [[('example', 'N', 0.979), ('tweet', 'V', 0.7763), ('1', '$', 0.9916)],no
#       [('example', 'N', 0.979), ('tweet', 'V', 0.7713), ('2', '$', 0.5832)]]
    def __init__(self,input,database='tweets'):
        n = 4 # n-gram
        self.m = n -1
        self.texts = input
        self.d = enchant.Dict("en_US")
        client = MongoClient('localhost', 27017)
        db = client[database]
        self.nodes = db['nodes']
        self.edges = db['edges']
        self.ovvLists = [[ind for ind,t in enumerate(text) if self.isOvv(t[0],t[1])] for text in self.texts]
        print self.ovvLists

    def isOvv(w,t):
#            if not isvalid(w):
        if t in [',','E','~','@','U']: # punctuation, emoticon, discourse marker, mention, url
            return False
        elif t in ['$',] or isMention(w): # Numeral or url or mention
            return False
        elif t in ['#'] or isHashtag(w):
            return False
        elif not isvalid(w) and t is not '&' :
            print '%s : %s is not ovv' %(t,w)
            return False
        else:
            return not self.d.check(w)


    def normAll(self):
        for ind,tweet in enumerate(self.texts): #ind indicates the tweet id
            if not self.ovvLists[ind]:
                continue
            self.norm(tweet,self.ovvLists[ind])

    def norm(self,tweet,ovvList):
        # ovvList is a list of numbers that indicates the index of the ovv word in the tweet
        for ovvInd in ovvList:
            ovvTag = tweet[ovvInd][1]
            ovv = tweet[ovvInd][0]
            #first we get the words that forms an ngram with the ovv
            candidates = returnCandRight(tweet)

    def returnCandRight(tweet):
        neighbours = tweet[ovvInd-self.m:ovvInd]
        for ind2,n in enumerate(neighbours):
            neighNode = n[0].strip()+'|'+n[1]
            # For each word next to ovv we look to the graph for candidates thatshares same distance and tag with the ovv
            distance = len(neighbours)-ind2
            # find all the non ovv nodes from the neighbour with same dis
            candidates = [edge['to'] for edge in self.edges.find({'from':neighNode,'dis': distance })]
            # filter candidates who has a different tag than ovv
            cands = filter(lambda x: self.nodes.find_one({'_id':x,'tag': ovvTag, 'ovv':False }), candidates)
            return cands
