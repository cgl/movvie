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
import enchant
class Reader():
    def __init__(path='None',format='None'):
        this.format=format
        this.path=path

    # Returns lot
    def read(file=None):
        if path:
            pass
        elif file:
            with open(infile) as l: 
                yield l[2]
    
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
    d = enchant.Dict("en_US")
    def __init(g)__:
        this.graph = g
        pass
    
    def getTweets(tweets):
        lot = CMUTweetTagger.runtagger_parse(tweets)
        #lot = [[('example', 'N', 0.979), ('tweet', 'V', 0.7763), ('1', '$', 0.9916)],
        #       [('example', 'N', 0.979), ('tweet', 'V', 0.7713), ('2', '$', 0.5832)]]
        for tweet in lot:
            getTweet(tweet)

    def getTweet(tweet):
        #tweet = [('example', 'N', 0.979), ('tweet', 'V', 0.7763), ('1', '$', 0.9916)]
        words = []
        for w,t,c in tweet:
            if ! this.graph.has_node(w):
                this.graph.add_node(w,ovv=False if d.check(w) else True)
                this.graph[w][t]=1
            else:
                if(this.graph[w].has_key(t)):
                    this.graph[w][t] +=1
                else:
                    this.graph[w][t] =1
            for x in words:
                if this.graph.has_edge(w,x):
                    # we added this one before, just increase the weight by one
                    G[w][x]['weight'] += 1
                else:
                    # new edge. add with weight=1
                    G.add_edge(subject_id, object_id, weight=1)
            words.append(w)
            
            

    def addNode(w):
        if(G.node.has_key(w)):
            return G.node
                
            
            
            
            
        
