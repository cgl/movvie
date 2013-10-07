#!/usr/bin/env python

def save():
    with open("/Users/cagil/Downloads/sample.txt") as f:
        f.readline()
        A = None
        U = None
        T = None
    
        for line in f:
            if line.split('\t')[0] == 'A':
                A = line.split('\t')[1]
            elif line.split('\t')[0] == 'U':
                U = line.split('\t')[1]
            elif line.split('\t')[0] == 'T':
                T = line.split('\t')[1]
                english = True
            elif english:
                yield (A,U,T)
    
    
