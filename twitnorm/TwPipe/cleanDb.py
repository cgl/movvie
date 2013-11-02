import normalizer
import CMUTweetTagger

def update_edges_tag(database='tweets_current'):
    tweets = [u"someone is cold game nd he needs to follow me",
          u"only 3mths left in school . i wil always mis my skull , frnds and my teachrs"]


    lot = CMUTweetTagger.runtagger_parse(tweets)

    N = normalizer.Normalizer(lot,database)
    tags = N.nodes.distinct('tag')
    for tag in tags:
        nouns = [node['_id'] for node in filter(lambda x: x['freq']> 8, N.nodes.find({'tag':tag}))]
        N.edges.update({'from': { '$in' : nouns}},{'$set' : {u'from_tag':tag } },multi=True)
        N.edges.update({'to': { '$in' : nouns}},{'$set' : {u'to_tag':tag } },multi=True)

def ensure_indexes(database='tweets_current'):
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client[database]

    db.edges.ensure_index([ ('from', 1), ('to', 1) , ('dis', 1 )] )
    db.edges.ensure_index('from_tag', 1)
    db.edges.ensure_index('to_tag', 1)
