#!/usr/bin/env python
# -*- Coding: utf-8 -*-
#Author: Cagil Ulusahin
#Date: October 12nd 2013
#
# 
# 
# 
#
# Sample input and output can be foun within the directory of the github project page.**  
#

import langid, getopt, sys, logging, os
import CMUTweetTagger
import networkx as nx
import enchant
import ast
import re
import sys, getopt
import langid
import logging
from pymongo import MongoClient

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT,filename='tweets.log',level=logging.DEBUG)

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
        logging.info('End Processing : %s', infile)

from memory_profiler import profile
@profile
def main(argv):
   infile = 'test/snap.sample'
#   outfile = 'test/test.graphml'
   path = None
   try:
      opts, args = getopt.getopt(argv,"hi:o:p:",["ifile=","ofile=","path="])
   except getopt.GetoptError:
      print 'graphlib.py -i <inputfile> -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'graphlib.py -i <inputfile> -o <outputfile>'
         print 'graphlib.py -p <path> -o <outputfile>'
         print 'Please check in.grapml, the initial graph will be read from that file'
         print ''
         sys.exit(1)
      elif opt in ("-i", "--ifile"):
         infile = arg
#      elif opt in ("-o", "--ofile"):
#         outfile = arg
      elif opt in ("-p", "--path"):
         path = arg
      
   T = MTweet()
   T.getTweets(infile)
#   print 'Constructed the graph now will write to file'
#   logging.info('Constructed the graph now will write to file : %s', outfile)
#   nx.write_graphml(T.graph,outfile)
#   logging.info('Finish write to file : %s', outfile)

'''
#    nx.write_gml(T.graph,'test/test-out.gml')
#    nx.write_gpickle(T.graph,'test/test-out.pckl')
   for a in T.graph.node:
       pass #print a
   print len(T.graph.node)
   return T.graph
'''
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
        lot = CMUTweetTagger.runtagger_parse(tweets)
        #lot = [[('example', 'N', 0.979), ('tweet', 'V', 0.7763), ('1', '$', 0.9916)],
        #       [('example', 'N', 0.979), ('tweet', 'V', 0.7713), ('2', '$', 0.5832)]]

        for tweet in lot:            
            self.getTweet(tweet)
        logging.info('Finish processing file : %s', outfile)

# t.getTweet([("This",'N', 0.979),("is",'N', 0.97),("@ahterx",'N', 0.979),("^^",'N', 0.979),("my",'N', 0.979),("luv",'N', 0.979)])
    def getTweet(self,tweet):
        #tweet = [('example', 'N', 0.979), ('tweet', 'V', 0.7763), ('1', '$', 0.9916)]
        words = []

        for w,t,c in tweet:
            if not self.isvalid(w):
                continue
            if w.startswith("http") or w.startswith("@") or w.startswith("#") or w.isdigit() or not w.isalnum():
                words.append('')
                continue
            self.addNode(w,t)
            for e,x in enumerate(reversed(words[-5:])):
                if x is not '':
                    self.incWeightOrCreateEdge(x,w,e)
            words.append(w)
        print words
        
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

    def isvalid(self,w):
    #return true if string contains any alphanumeric keywors
        return bool(re.search('[A-Za-z0-9]', w))

class Tweet:
    def __init__(self,g=None):
        if g is None:
#            self.graph = nx.read_gml('test/test.gml')
            self.graph = nx.read_graphml('in.graphml')
#            self.graph = nx.read_gpickle('test/test.pckl')
            print 'Graph has been read from file'
        else:
            self.graph = g
        self.d = enchant.Dict("en_US")
    
    def getTweets(self,infile):
        r = Reader()   
        tweets = [unicode(a) for a in r.read(file=infile)]
        lot = CMUTweetTagger.runtagger_parse(tweets)
        #lot = [[('example', 'N', 0.979), ('tweet', 'V', 0.7763), ('1', '$', 0.9916)],
        #       [('example', 'N', 0.979), ('tweet', 'V', 0.7713), ('2', '$', 0.5832)]]

        for tweet in lot:            
            self.getTweet(tweet)

    def getTweet(self,tweet):
        #tweet = [('example', 'N', 0.979), ('tweet', 'V', 0.7763), ('1', '$', 0.9916)]
        words = []

        for w,t,c in tweet:
            if (not self.isvalid(w)) or w.startswith("http") or w.startswith("@") or w.startswith("#") or w.isdigit() or not w.isalnum():
                continue
            self.addNode(w,t)
            for x in words:
                if self.graph.has_edge(w,x):
                    # we added this one before, just increase the weight by one
                    self.graph.add_edge(w,x)
                    self.graph[w][x]['weight'] += 1
                else:
                    # new edge. add with weight=1
                    self.graph.add_edge(w,x, weight=1)
            words.append(w)

    #adds node with the pos tag t to the self.graph
    def addNode(self,w,t):
        if not self.graph.has_node(w):
            self.graph.add_node(w,ovv=False if self.d.check(w) else True)
            self.graph.node[w][t]=1
        else:
            if(self.graph.node[w].has_key(t)):
                self.graph.node[w][t] += 1
            else:
                self.graph.node[w][t] = 1

    def isvalid(self,w):
    #return true if string contains any alphanumeric keywors
        return bool(re.search('[A-Za-z0-9]', w))

if __name__ == "__main__":
    logging.info('Start Processing')
    try:
        main(sys.argv[1:])    
    except Exception, e:
        logging.error(str(e))
        sys.exit(0)
    logging.info('End Processing')
                
def gen_walk(path='.'):
    for dirname, dirnames, filenames in os.walk(path):
        # print path to all subdirectories first.
        #for subdirname in dirnames:
        #            print os.path.join(dirname, subdirname)

        # print path to all filenames.
        for filename in filenames:
            yield os.path.join(dirname, filename)

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if '.git' in dirnames:
            # don't go into any .git directories.
            dirnames.remove('.git')

            
            
            
            
        

'''    
from graph_tool.all import *
class WordGraph():
    def createGraph():
        g = Graph(directed=False)
        v1 = g.add_vertex()
        v2 = g.add_vertex()
        e = g.add_edge(v1, v2)
        vlist = g.add_vertex(10)
        weight = g.new_edge_property("double") 
        weight[e] = 3.1416
        g.edge_properties["weight"] = weight
    
    def iterate(g):
        for v in g.vertices():
            print(v)
        for e in g.edges():
            print(e)
    def save(g):
        g.save("my_graph.xml.gz")
    def load():
        g2 = load_graph("my_graph.xml.gz")
        return g2
'''
