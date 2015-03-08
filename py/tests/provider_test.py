import unittest
import provider

_demo_graph = [("a","b"), ("a","c"), ("a","d"), ("d","e"),
               ("b","a"), ("c","a"), ("d","a"), ("e","d")];

class ListProviderTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_index(self):
        el = provider.EdgeList(_demo_graph)
        self.assertEqual(el["a"], 0)
        self.assertEqual(el["b"], 1)
        self.assertEqual(len(el), 5)

    def test_len(self):
        # is actually the same test as test_index, just to see if there's an
        # instantiation error.
        el2 = provider.EdgeList(_demo_graph)
        self.assertEqual(el2["a"], 0)
        self.assertEqual(el2["b"], 1)
        self.assertEqual(len(el2), 5)

    def test_adj(self):
        el = provider.EdgeList(_demo_graph)
        adj = el.adj()
        self.assertEqual((5,5),adj.shape)
        self.assertEqual(provider.csr_matrix, type(adj))
