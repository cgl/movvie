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

import langid, getopt, sys, logging, os, socket
import CMUTweetTagger
import networkx as nx
class Reader():
    def __init__(format):
        format=format
    
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

class Tweet:
    def __init()__:
        pass
    
    def getTweets(tweets):
        lot = CMUTweetTagger.runtagger_parse(tweets)
        #lot = [[('example', 'N', 0.979), ('tweet', 'V', 0.7763), ('1', '$', 0.9916)],
        #       [('example', 'N', 0.979), ('tweet', 'V', 0.7713), ('2', '$', 0.5832)]]
        for tweet in lot:
            getTweet(tweet)

    def getTweet(tweet):
        #tweet = [('example', 'N', 0.979), ('tweet', 'V', 0.7763), ('1', '$', 0.9916)]
        for w,t,c in tweet:
            
            
        
d = {'host': socket.gethostname(),}
FORMAT = '%(asctime)-15s %(host)s -8s %(message)s'
logging.basicConfig(format=FORMAT,filename='filtering.log',level=logging.DEBUG)

def read_tweets(lang='en',infile='snap.sample'):
    with open(infile) as f:        
        A = None
        U = None
        T = None
        english = None
        for line in f:
            if line.split('\t')[0] == 'T':
                T = line.split('\t')[1].strip('\n')
            elif line.split('\t')[0] == 'U':
                U = line.split('\t')[1].strip('\n')
            elif line.split('\t')[0] == 'W':
                W = line.split('\t')[1].strip('\n')
                if not (W is None) | (W == 'No Post Title'):
                    if langid.classify(W)[0] == lang:
                        english = True
            elif english:
                yield T,U,W
                english=False

def write_tweets(lang='en',infile='snap.sample',outfile='out.txt'):
    logger = logging.getLogger('tcpserver')
    logger.info('Started Processing : %s', infile , extra=d)
    try:
        tweets = read_tweets(lang=lang,infile=infile)
        f = open(outfile,"w")
        for chunk in tweets:
            f.write(str(chunk)+'\n')
        f.close()
    except Exception, e:
        logger.error(str(e),extra=d)
        return
    logger.info('End Processing : %s', infile , extra=d)
    

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hliop:v", ["help", "language=", "input_file=", "output_file=","path="])
    except getopt.GetoptError, err:
        print str(err) # will print an error about option not recognized..
        sys.exit(1)
    # Default option values
    lang='en'
    infile='snap.sample'
    outfile='out.txt'
    verbose = False
    # Process cmd line options
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif o in ("-l", "--language"):
            lang = a
        elif o in ("-i", "--input_file"):
            infile = a
        elif o in ("-o", "--output_file"):
            outfile = a
        elif o in ("-p", "--path"):
            files = gen_walk(a)
            for e,f in enumerate(files):
                folder = '/'.join(f.split("/")[:-1])
                os.system("mkdir -p out/%s" %folder )
                write_tweets(lang=lang,infile=f,outfile='out/%s' % (f))
            return
        else:
            assert False, "unhandled option!"    
    write_tweets(lang=lang,infile=infile,outfile=outfile)

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

def usage():
    print 'python script.py [--language="en"] [--input_file="/home/cagil/Datasets/snap/snap.sample"] [--output_file="output_en.txt"]'
    print 'ex: python languagefiltering.py --language="en" --input_file="/home/cagil/Datasets/snap/tweets2009-07.txt" --output_file="output_en_07.txt"'
    print 'ex: python languagefiltering.py --path=test2/'
if __name__ == "__main__":
    main()    

import os
def gen_walk(path='.'):
    for dirname, dirnames, filenames in os.walk(path):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            print os.path.join(dirname, subdirname)

        # print path to all filenames.
        for filename in filenames:
            yield os.path.join(dirname, filename)

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if '.git' in dirnames:
            # don't go into any .git directories.
            dirnames.remove('.git')
