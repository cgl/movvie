import re
import os
import fuzzy
import constants
import CMUTweetTagger
from pymongo import MongoClient
from numpy import array
import pickle

CLIENT = MongoClient('localhost', 27017)
DB = CLIENT['tweets']

def top_n(res,n=100,verbose=False):
    in_top_n = 0
    total_ill = 0
    index_list = {}
    for res_ind in range(0,len(res)):
        answer = constants.mapping[res_ind][1]
        ovv = constants.mapping[res_ind][0]
        if answer != ovv:
            total_ill += 1
            if res[res_ind]:
                res_list = [a[0] for a in res[res_ind][:n]]
                if answer in res_list:
                    in_top_n += 1
                    ind = res_list.index(answer)
                    index_list_n = index_list.get(ind,[0,[]])
                    index_list_n[0] += 1
                    index_list_n[1].append(res_ind)
                    index_list[ind] = index_list_n
    print 'Out of %d, %d has an normalization, we^ve %d of those correct normalizations in our list with indexes %s' % (len(res),total_ill, in_top_n,[(a, index_list[a][0]) for a in index_list])
    if verbose:
        for a in index_list:
            if a != 0:
                print  [ (b,a,res[b][a][0]) for b in index_list[a][1]]
    return index_list

def get_node(word,tag=None):
    if tag is None:
        return [DB.nodes.find_one({'_id':word+"|"+a}) for a in constants.tags if DB.nodes.find_one({'_id':word+"|"+a})]
    else:
        return DB.nodes.find_one({'_id':word+"|"+tag})

def max_values(res):
    correct_results = []
    for ind in range(0,len(res)):
        if res[ind]:
            if res[ind][0][0] == constants.mapping[ind][1]:
                correct_result = res[ind][0]
                correct_results.append(correct_result[1:])
    arr = array(correct_results)
    return arr.max(axis=0)

def dump_to_file(matrix,filename="matrix2.txt"):
    with open(filename, 'wb') as mfile:
        pickle.dump(matrix,mfile)


def load_from_file(filename="matrix2.txt"):
    with open(filename, 'rb') as mfile:
        matrix = pickle.load(mfile)
    return matrix

def isvalid(w):
    #return true if string contains any alphanumeric keywors
        return bool(re.search('[A-Za-z0-9]', w))

def isMention(w):
    #
    # N @CIRAME --> True
    # P @       --> False
    return len(w) > 1 and w.startswith("@")

def isHashtag(w):
    return w.startswith("#")

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
