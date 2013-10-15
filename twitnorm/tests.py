"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from graphlib import Reader,Tweet
import networkx as nx

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_graphlib(self):
        r = Reader()
        lot  = [unicode(a) for a in r.read(file='test/snap.sample')]
        T = Tweet()
        T.getTweets(lot)
        for a in T.graph.node:
            print a
    #    nx.write_gml(T.graph,'test/test-out.gml')
        nx.write_graphml(T.graph,'test/test.graphml')
    #    nx.write_gpickle(T.graph,'tes/test-out.pckl')
        print len(T.graph.node)
        return True
