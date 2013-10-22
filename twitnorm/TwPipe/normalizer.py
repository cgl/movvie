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
        for ind,tweet in enumerate(self.texts):
            if not self.ovvLists[ind]:
                continue
            self.norm(tweet,self.ovvLists[ind])
            
    def norm(self,tweet,ovvList):
            for ind,w in enumerate(ovvList):
                neighbours = tweet[ind-self.m:ind] 
                for ind2,n in enumerate(neighbours):
                    distance = len(neighbours)-ind2
                    print distance
                    print 'from %s ' % n[0]
  #                  print  self.edges.count()
#                    for a in self.edges.find({'from':n[0],'dis': distance }):
 #                       print a
                                                         
                    candidates = [edge['to']
                                  for edge in self.edges.find({'from':n[0]+'|'+n[1],'dis': distance })
                                    ]
                    print 'candidates:'
                    print candidates
                    cands = filter(lambda x: x.endswith('|'+tweet[ind][1]),candidates)
#                    filter(lambda x: self.nodes.find_one({'tag':, 'ovv':False }), candidates)
   
                    print 'Filtered candidates:'
                    print cands
                neighbours = tweet[ind+1:ind+1+self.m]
                for ind2,n in enumerate(neighbours):
                    candidates = [edge['to'] for edge in self.edges.find({'from':n,'dis': ind2+1 })]
                    cands = filter(lambda x: self.nodes.find_one({'_id':x, 'ovv':False, 'tag_'+tweet[ind][1] : { '$gt' : 1 } }), candidates)
                    print candidates
                    print cands
    
    
