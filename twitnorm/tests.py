"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from graphlib import Reader,Tweet,MTweet
import networkx as nx

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_graphlib_mongo(self):
        T = MTweet(database='test_database')
        T.nodes.remove()
        print T.nodes.count()
        T.getTweets('test/snap.sample')
        print T.nodes.count()
        return T.nodes.find_one({'weight':0}) is None

'''
def old_test_graphlib(self):
        T = Tweet()
        T.getTweets('test/snap.sample')
#        for a in T.graph.node:
#            print a
    #    nx.write_gml(T.graph,'test/test-out.gml')
        nx.write_graphml(T.graph,'test/test.graphml')
    #    nx.write_gpickle(T.graph,'tes/test-out.pckl')
        print len(T.graph.node)
        return True

def sample_mongo():
        a= t.nodes.find({'_id': 'man'},{ 'edges': {"$elemMatch": {'dis': 2, 'id': u'Paris'} }})
        b = a.next()
        print b['edges'][0]['weight']
'''
