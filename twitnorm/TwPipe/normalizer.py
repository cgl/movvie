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
        self.ovvLists = [[ind for ind,t in enumerate(text) if not self.d.check(t[0])] for text in self.texts]

    def normAll(self):
        for ind,tweet in enumerate(self.texts): #ind indicates the tweet id
            if not self.ovvLists[ind]:
                continue
            self.norm(tweet,self.ovvLists[ind])

    def norm(self,tweet,ovvList):
        # ovvList is a list of numbers that indicates the index of the ovv word in the tweet
        print tweet
        for ovvInd in ovvList:
            ovvTag = tweet[ovvInd][1]
            ovv = tweet[ovvInd][0]
            print 'ovv tag is %s ' %ovvTag
            #first we get the words that forms an ngram with the ovv
            neighbours = tweet[ovvInd-self.m:ovvInd]
            for ind2,n in enumerate(neighbours):
                neighNode = n[0].strip()+'|'+n[1]
                # For each word next to ovv we look to the graph for candidates thatshares same distance and tag with the ovv
                distance = len(neighbours)-ind2
                print 'from %s ' % neighNode
                '''
                for a in self.edges.find({'from':neighNode,'dis': distance }):
                    print a
                    '''
                # find all the non ovv nodes from the neighbour with same dis
                candidates = [edge['to']
                    for edge in self.edges.find({'from':neighNode,'dis': distance })]
                print 'candidates:'
                print candidates[:100]
                # filter candidates who has a different tag than ovv
#                cands = filter(lambda x: x.endswith('|'+ovvTag),candidates)
                cands = filter(lambda x: self.nodes.find_one({'_id':x,'tag': ovvTag, 'ovv':False }), candidates)
                print 'Filtered candidates for %s:' %ovv
                print cands[:100]


