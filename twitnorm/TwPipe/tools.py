import re
import os
import fuzzy

salient=0.00000000001


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
