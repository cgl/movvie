#!/usr/bin/env python
# -*- Coding: utf-8 -*-
#Author: Cagil Ulusahin
#Date: October 7th 2013
#
# A small yet fast parser to filter the SNAP 467 million Twitter dataset[1] by language.
# 
# For language detection the langid*[2] is used.
#
# Sample input and output can be foun within the directory of the github project page.**  
#
# [1] J. Yang, J. Leskovec. Temporal Variation in Online Media. ACM International Conference on Web Search and Data Mining (WSDM '11), 2011.
# [2] Lui, Marco and Timothy Baldwin (2012) langid.py: An Off-the-shelf Language Identification Tool, In Proceedings of the 50th Annual Meeting of the Association for Computational Linguistics (ACL 2012), Demo Session, Jeju, Republic of Korea. Available from www.aclweb.org/anthology/P12-3005
# * https://github.com/saffsd/langid.py
# ** https://github.com/cgl/movvie/tree/master/twitnorm

import langid, getopt, sys, logging, os, socket
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
