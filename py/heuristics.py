# Heuristics implementations are found in this package.

import networkx as nx

class Maxdepth:
    """Heuristics are totally decopuled from the main algorithm.

    Using and linking them together is, however, trivial and even elegant.

    This is the Maximum Depth Heuristic. It uses networkx for the graph
    algorithms.
    """
    def __init__(self,edgelist, depth):
        self.g = nx.DiGraph()
        self.g.add_edges_from(edgelist)
        self.depth = depth
        self._pairs = None

    def top(self,nodes=None):
        """The first time this function is run, the heuristic is computed
        for the whole graph and result is saved.

        If nodes==Node or a list
            - it returns a dict of form {from_node: [list_of_to_nodes]}
        Otherwise,
            - it returns a list of _to_ nodes.
        """

        if self._pairs is None:
            p = nx.all_pairs_shortest_path_length(self.g, self.depth)
            self._pairs = {k: [i for i,_ in tos.items()] for k, tos in p.items()}

        if nodes is None:
            return self._pairs
        if not isinstance(nodes, list):
            return self._pairs[nodes]
        return {k: self._pairs[k] for k in nodes }

    def topGen(self, nodes=None):
        """It uses top(), but instead of returning the result, it is a generator
        function that (always) yields pairs of nodes."""
        res = self.top(nodes)

        if isinstance(res, list):
            for i in res:
                yield((nodes, i))

        else:
            for i,l in res.items():
                for j in l:
                    yield((i,j))
