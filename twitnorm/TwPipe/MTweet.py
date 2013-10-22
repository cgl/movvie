import langid, getopt, sys, logging, os
import CMUTweetTagger
import enchant
import ast
import langid
from pymongo import MongoClient

from tools import *

class MTweet:
    def __init__(self,database='tweets'):
        self.d = enchant.Dict("en_US")
        client = MongoClient('localhost', 27017)
        db = client[database]
        self.nodes = db['nodes']
        self.edges = db['edges']

    def getTweets(self,infile):
        r = Reader()   
        tweets = [unicode(a) for a in r.read(file=infile)]
        logging.info('Tweets are read from : %s', infile)
        lot = CMUTweetTagger.runtagger_parse(tweets)
        logging.info('CMUTagger has parsed the tweets')
        #lot = [[('example', 'N', 0.979), ('tweet', 'V', 0.7763), ('1', '$', 0.9916)],
        #       [('example', 'N', 0.979), ('tweet', 'V', 0.7713), ('2', '$', 0.5832)]]

        for tweet in lot:            
            self.getTweet(tweet)
        logging.info('Finish processing file : %s', infile)

# t.getTweet([("This",'N', 0.979),("is",'N', 0.97),("@ahterx",'N', 0.979),("^^",'N', 0.979),("my",'N', 0.979),("luv",'N', 0.979)])
    def getTweet(self,tweet):
        #tweet = [('example', 'N', 0.979), ('tweet', 'V', 0.7763), ('1', '$', 0.9916)]
        words = []

        for w,t,c in tweet:
#            if not isvalid(w):
            if t in [',','E','~']:                
                continue
            elif t in ['U','$','@',] or isMention(w): # Numeral or url or mention               
                words.append('')
                continue
            elif t in ['#'] or isHashtag(w):
                words.append(w.strip('#'))
                continue
            elif not isvalid(w) and t is not '&' :
                print '%s : %s' %(t,w)
                words.append('')
                continue
            # 'G','&','P'
            self.addNode(w,t)
            for e,x in enumerate(reversed(words[-5:])):
                if x is not '':
                    self.incWeightOrCreateEdge(x,w,e)
            words.append(w)
        
    def incWeightOrCreateEdge(self,n1,n2,d):
        query = {'from':n1,'to':n2,'dis':d}
        query2 = {'from':n2,'to':n1,'dis':d}
        if self.edges.find_one(query) is None:
            self.edges.insert({'from':n1,'to':n2,'dis':d, 'weight':1})
            self.edges.insert({'from':n2,'to':n1,'dis':d, 'weight':1})
        else:
            i1 = self.edges.update(query, {"$inc" : {"weight" :1} })
            i2 = self.edges.update(query2, {"$inc" : {"weight" :1} })
            if not i2['updatedExisting']:
                self.edges.insert({'from':n2,'to':n1,'dis':d, 'weight':1})
            

    # Creates edge if not present
    def incrementEdgeWeight(self,n1,n2,d):
        query = {'_id': n1, 'edges': {"$elemMatch": {'dis': d, 'name': n2} }}
        if self.nodes.find_one(query) is None:
            self.nodes.update( {'_id': n1 },
                           { '$addToSet': { "edges" : {"name":n2,"dis":d,'weight':0 }} },False)
        self.nodes.update( query,
                       { "$inc" :
                             { "edges.$.weight" : 1 }
                         })                                              

        '''
        obj = self.edges.find_one({"_id":w})
        if self.graph.has_edge(w,x):
            # we added this one before, just increase the weight by one
            self.graph.add_edge(w,x)
            self.graph[w][x]['weight'] += 1
        else:
            # new edge. add with weight=1
            self.graph.add_edge(w,x, weight=1)
            '''

    #adds node with the pos tag t to the self.graph
    def addNode(self,w,t):
        tag = "tag_"+t
        obj = self.nodes.find_one({"_id":w})
        if obj is None:
            obj_id = self.nodes.insert({"_id":w,"freq":1,tag:1,"ovv":False if self.d.check(w) else True })
        else:
            obj["freq"] += 1
            if(obj.has_key(tag)):
                obj[tag] += 1
            else:
                obj[tag] = 1
            self.nodes.save(obj)

class Reader():
    def __init__(self,path=None,format=None):
        self.format=format
        self.path=path

    # Returns lot
    def read(self,file=None):
        if self.path is not None:
            files = gen_walk(path)
            for e,f in enumerate(files):
                folder = '/'.join(f.split("/")[:-1])
                os.system("mkdir -p out/%s" %folder )
                lot = self.readFile_direct(f)
                os.remove(f)
        elif file:
            print file
            lot = self.readFile_direct(file)
        return lot

    def readFile(self,f):
        with open(file) as f: 
            for line in f:
                yield ast.literal_eval(line)[2]

    def readFile_direct(self,infile,lang='en'):
        logging.info('Started Processing : %s', infile)
        with open(infile) as f:        
            W = None
            for line in f:
                if line.split('\t')[0] == 'W':
                    W = line.split('\t')[1].strip('\n').decode('utf-8')
                    if not (W is None) | (W == 'No Post Title'):
                        if langid.classify(W)[0] == lang:                                
                            yield W
        logging.info('File : %s has been yielded', infile)
           
