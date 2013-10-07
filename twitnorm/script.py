#!/usr/bin/env python
# -*- Coding: utf-8 -*-
#Author: Cagil Ulusahin
#Date: October 7th 2013
import langid, getopt, sys

def read_tweets(lang='en',infile='snap.sample'):
    with open(infile) as f:
        f.readline()
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
    tweets = read_tweets(lang=lang,infile=infile)
    f = open(outfile,"w")
    for chunk in tweets:
            f.write(str(chunk)+'\n')
    f.close()

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hlio:v", ["help", "language=", "input_file=", "output_file="])
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
        else:
            assert False, "unhandled option!"
    write_tweets(lang=lang,infile=infile,outfile=outfile)

if __name__ == "__main__":
    main()    
