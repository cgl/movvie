import normalizer
import CMUTweetTagger

#use tweets
#db.copyDatabase("tweets","tweets_current","localhost")
def update_edges_tag(database='tweets_current'):
    tweets = [u"someone is cold game nd he needs to follow me",
          u"only 3mths left in school . i wil always mis my skull , frnds and my teachrs"]


    lot = CMUTweetTagger.runtagger_parse(tweets)

    norm = normalizer.Normalizer(lot,database)
    tags = norm.nodes.distinct('tag')
    for tag in tags:
        nouns = [node['_id'] for node in filter(lambda x: x['freq']> 8, norm.nodes.find({'tag':tag}))]
        norm.edges.update({'from': { '$in' : nouns}},{'$set' : {u'from_tag':tag } },multi=True)
        norm.edges.update({'to': { '$in' : nouns}},{'$set' : {u'to_tag':tag } },multi=True)

def ensure_indexes(database='tweets_current'):
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client[database]

    db.edges.ensure_index([ ('from', 1), ('to', 1) , ('dis', 1 )] )
    db.edges.ensure_index('from_tag', 1)
    db.edges.ensure_index('to_tag', 1)

if __name__ == "__main__":
    update_edges_tag()
