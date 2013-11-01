import CMUTweetTagger
from normalizer import Normalizer

def han(infile = 'test/corpus.tweet'):
    results = []
    tweet = []
    lot = []
    tweet_text = []
    import codecs
    with codecs.open(infile) as han_file:
        han_file.readline()
        for line in han_file:
            if not line.strip('\n').isdigit():
                try:
                    line = line.strip('\n').decode()
                    line_strip = line.split('\t')
                    tweet.append((line_strip[0], line_strip[1], line_strip[2]))
                    tweet_text.append(line_strip[0])
                except UnicodeDecodeError:
                    tweet.append((',,,', line_strip[1], ',,,'))
                    tweet_text.append(',,,')
            else:
                results.append(tweet)
                lot.append(' '.join(tweet_text))
                tweet = []
                tweet_text = []
    return lot, results

def bisi():
    tweets , results = han()
    lot =  CMUTweetTagger.runtagger_parse(tweets)
    norm = Normalizer(lot)
    our_results = norm.normalizeAll()
    test = []
    reference = []
    for tweetInd, tweet in enumerate(results):
        for ind, word in enumerate(tweet):
#            if our_results[tweetInd][ind][1] == 'OOV':
            if results[tweetInd][ind][1] == 'OOV':
                reference.append(results[tweetInd][ind][2])
                test.append(our_results[tweetInd][ind][2])
    from sets import Set
    import nltk
    set_reference = Set(reference)
    set_test = Set(test)
    p = nltk.metrics.scores.precision(set_reference,set_test )
    print 'Precision: %f' % p
    r = nltk.metrics.scores.recall(set_reference,set_test )
    print 'Recall: %f' % r
    f_m = nltk.metrics.scores.f_measure(set_reference,set_test )
    print 'F-measure: %f' % f_m
    return reference,test


def calculateRecall():
    return 0

def calculatePrecision():
    return 0

def calculateFmeasure():
    return 0
