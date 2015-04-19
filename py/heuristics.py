# Heuristics implementations using sparse graphs here.
# Using heuristics needs the original adjacency matrix stored.

import networkx as nx

class Maxdepth:
    """Heuristics are totally decopuled from the main algorithm.

    Using and linking them together is, however, trivial and even elegant.
    """
    def __init__(self,edgelist, depth):
        self.g = nx.DiGraph()
        self.g.add_edges_from(edgelist)
        self.depth = depth
        self._pairs = None

    def top(self,nodes=None):
        """Yields (from,to) pairs. Arguments can be:
        - no arguments: Apply heuristic for all graph.
        - a node: Applies heuristic on that node only.
        - a list of nodes: Applies heuristic on all nodes of the list."""

        if self._pairs is None:
            print("Computing HEU")
            p = nx.all_pairs_shortest_path_length(self.g, self.depth) 
            self._pairs = {k: [i for i,_ in tos.items()] for k, tos in p.items()}

        if nodes is None:
            return self._pairs
        if not isinstance(nodes, list):
            return self._pairs[nodes]
        return {k: self._pairs[k] for k in nodes }

    def topGen(self, nodes=None):
        res = self.top(nodes)

        if isinstance(res, list):
            for i in res:
                yield((nodes, i))

        else:
            for i,l in res.items():
                for j in l:
                    yield((i,j))

