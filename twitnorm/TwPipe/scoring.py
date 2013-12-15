import CMUTweetTagger
from normalizer import Normalizer
import traceback


def han(numOfResults,infile = 'test/corpus.tweet'):
    results = []
    tweet = []
    lot = []
    tweet_text = []
    import codecs
    with codecs.open(infile) as han_file:
        han_file.readline()
        for  line in  han_file:
            if len(lot) >= numOfResults:
                break
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

def pennel(numOfResults,infile,reffile):
    results = []
    tweet = []
    lot = []
    tweet_text = []
    import codecs
    with codecs.open(infile) as pennel_hyp_file, codecs.open(reffile) as pennel_ref_file:
        for  line in  pennel_hyp_file:
            if len(lot) >= numOfResults:
                break
            try:
                line = line.strip('\n').decode()
                line_strip = line.split(' ')
                correct_answer = pennel_ref_file.next().split(' ')[2]
                for ind,word in enumerate(line_strip):
                    if ind == 2:
                        tweet.append((word,"OOV",correct_answer))
                    elif word == "<s>" or word == "</s>":
                        continue
                    else:
                        tweet.append((word,"IV",word))
                    tweet_text.append(word)
            except:
                print line
                print traceback.format_exc()

            results.append(tweet)
            lot.append(' '.join(tweet_text))
            tweet = []
            tweet_text = []
    return lot, results

def bisi(numOfResults=548):
    tweets , results = han(numOfResults)

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
                if (results[tweetInd][ind][2] != our_results[tweetInd][ind][2]):
                    print '%s \t %s \t %s ' % (results[tweetInd][ind][0] , our_results[tweetInd][ind][2],results[tweetInd][ind][2])
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
