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


# argv = ['-i', 'test/snap.sample', '--database=test', '-m', '4']
def main(argv):
    print argv
    infile = 'test/snap.sample'
    database = 'tweets'
    max_dis = 4
    try:
        opts, args = getopt.getopt(argv,"hi:db:m:p:",["ifile=","database=","max_dis=","path="])
    except getopt.GetoptError:
        print 'graphlib.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'graphlib.py -i <inputfile> -d tweets -m 4'
            print ''
            sys.exit(1)
        elif opt in ("-i", "--ifile"):
            infile = arg
        elif opt in ("-db", "--database"):
            database = arg
        elif opt in ("-m", "--max_dis"):
            max_dis = int(arg)
        elif opt in ("-p", "--path"):
            pass

    twt = MTweet(database,max_dis,infile)
    twt.get_raw_tweets()

#    matrix1 = analysis.calc_score_matrix(constants.pos_tagged,constants.results,analysis.ovvFunc,database=database)

if __name__ == "__main__":
    logging.info('Start Processing')
    try:
        main(sys.argv[1:])
        logging.info('End Processing Succesfully')
    except Exception, exc:
        logging.error(str(exc),exc_info=True)
        logging.error('End Processing Failure')
        sys.exit(0)
