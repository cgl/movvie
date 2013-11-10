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
import enchant
import ast
import re
import sys, getopt
import langid
import logging
from pymongo import MongoClient
from MTweet import MTweet
from tools import *

FORMAT = '%(asctime)-12s (%(process)d) %(message)s'
ERROR_FORMAT = '%(asctime)-12s (%(process)d) %(message)s'
logging.basicConfig(format=FORMAT,filename='tweets.log',level=logging.DEBUG)



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


if __name__ == "__main__":
    logging.info('Start Processing')
    try:
        main(sys.argv[1:])
        logging.info('End Processing Succesfully')
    except Exception, e:
        logging.error(str(e),exc_info=True)
        logging.error('End Processing Failure')
        sys.exit(0)







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
