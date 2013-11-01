## to fill in the db
import graphlib
graphlib.main('test/snap.sample')

tweets = [u"someone is cold game nd he needs to follow me",
          u"only 3mths left in school . i wil always mis my skull , frnds and my teachrs"]

import CMUTweetTagger ; lot = CMUTweetTagger.runtagger_parse(tweets)

N = normalizer.Normalizer(lot)


reload(normalizer); N = normalizer.Normalizer(lot) ; b= N.normalizeAll()

reload(normalizer);reload(scoring); lot = scoring.bisi()
