# -*- coding: utf-8 -*-
import langid, getopt, sys, logging, os
import CMUTweetTagger
import enchant
import ast
import langid
from pymongo import MongoClient
from decimal import Decimal
from tools import isMention, isHashtag, isvalid, gen_walk, parseTweets, spell_check

# tags : http://www.ark.cs.cmu.edu/TweetNLP/gimpel+etal.acl11.pdf

class MTweet:
    def __init__(self, database, max_dis, infile):
        self.dict = enchant.Dict("en_US")
        client = MongoClient('localhost',  27017)
        dtb = client[database]
        self.nodes = dtb['nodes']
        self.edges = dtb['edges']
        self.completed = Decimal(0)
        self.infile = infile
        self.max_dis = max_dis

    def get_raw_tweets(self):
        rdr = Reader()
        raw_tweets = rdr.read(infile=self.infile)
        lo_rt = []
        number_of_tweets = 0
        for raw_tweet in raw_tweets:
            lo_rt.append(unicode(raw_tweet))
            number_of_tweets += 1
            if number_of_tweets == 1000:
                self.parse_raw_tweets(lo_rt)
                number_of_tweets = 0
                lo_rt = []
        self.parse_raw_tweets(lo_rt)
        logging.info('Finished tokenizing tweets from : %s',  self.infile)

    def parse_raw_tweets(self,lo_rt):
        lot = parseTweets(lo_rt)
        self.getTweets(lot,self.max_dis)

    def getTweets(self, lot, max_dis):
        logging.info('CMUTagger has parsed the tweets from : %s',  self.infile)
        #lot = [[('example',  'N',  0.979),  ('tweet',  'V',  0.7763),  ('1',  '$',  0.9916)],
        #       [('example',  'N',  0.979),  ('tweet',  'V',  0.7713),  ('2',  '$',  0.5832)]]

        try:
            for tweet in lot:
                self.getTweet(tweet,max_dis)
                self.completed += 1
        except Exception, e:
            logging.error('[%d]'%self.completed+str(e),exc_info=True)
        logging.info('Finish processing [%d] tweets from : %s', self.completed, self.infile)
        logging.info('Node count:%d Edge count:%d after processing %s',  self.nodes.count(), self.edges.count(), self.infile)


    # t.getTweet([("This", 'N',  0.979), ("is", 'N',  0.97), ("@ahterx", 'N',  0.979),
    #("^^", 'N',  0.979), ("my", 'N',  0.979), ("luv", 'N',  0.979)])
    def getTweet(self, tweet,max_dis):
        #tweet = [('example',  'N',  0.979),  ('tweet',  'V',  0.7763),  ('1',  '$',  0.9916)]
        words = []

        for word, tag, conf in tweet:
            word = word.lower()
#            if not isvalid(word):
            if tag in [',', 'E', '~'] or (not isvalid(word) and tag is not '&'):
                # print '%s : %s' %(tag, word) # G : |: , ^ : (****), G : ♫, P : @, G : ~ , G : :: , G : - not_valid and &
                # , : ... ! ? [ ] ( ) : " all tagged as ","
                continue
            elif (tag is '$' and not word.isalpha()):
                words.append('')
                continue
            elif tag in ['U', '@' ] or isMention(word): # Numeral or url or mention
                words.append('')
                continue
            elif tag in ['#'] or isHashtag(word):
                words.append((word.strip('#'), tag, conf))
                continue
            # 'G', '&', 'P'
            self.addNode(word, tag)
            for e, x in enumerate(reversed(words[-max_dis:])): # max_dis was 5
                if x is not '':
                    self.incWeightOrCreateEdge(x[0].strip(), word.strip(), e,
                                               x[1].strip(), tag.strip(), (x[2]+conf)/2)
            words.append((word, tag, conf))

    def incWeightOrCreateEdge(self, n1, n2, d, tn1, tn2, wght):
        node1 = n1
        node2 = n2
        query = {'from':node1, 'to':node2, 'dis':d, "from_tag": tn1,"to_tag": tn2, }
        if self.edges.find_one(query) is None:
            query['weight'] = wght
            self.edges.insert(query)
        else:
            self.edges.update(query,  {"$inc" : {"weight" :wght} })

    #adds node with the pos tag t to the self.graph
    def addNode(self, word, tag):
        node = word
        obj = self.nodes.find_one({"node":node,"tag":tag})
        if obj is None:
            ovv = not spell_check(word)
            self.nodes.insert({"node":node, "freq":1, 'tag':tag, "ovv": ovv })
        else:
            self.nodes.update({"node":node,"tag":tag}, {'$inc': {"freq" : 1 }})

class Reader():
    def __init__(self, path=None, input_format=None):
        self.format = input_format
        self.path = path

    # Returns lot
    def read(self, infile=None):
        if self.path is not None:
            files = gen_walk(self.path)
            for e, f in enumerate(files):
                folder = '/'.join(f.split("/")[:-1])
                os.system("mkdir -p out/%s" %folder )
                lot = self.read_file_direct(f)
                os.remove(f)
        elif infile:
            print infile
            lot = self.read_file_direct(infile)
        return lot

    def readFile(self, infile):
        with open(infile) as f:
            for line in f:
                yield ast.literal_eval(line)[2]

    def read_file_direct(self, infile, lang='en'):
        logging.info('Started Processing : %s',  infile)
        with open(infile) as f:
            W = None
            for line in f:
                if line.split('\t')[0] == 'W':
                    W = line.split('\t')[1].strip('\n').decode('utf-8')
                    if not (W is None) | (W == 'No Post Title'):
                        if langid.classify(W)[0] == lang:
                            yield W
        logging.info('File : %s has been yielded', infile)
