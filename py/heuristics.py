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

    def top(self,nodes=None):
        """Yields (from,to) pairs. Arguments can be:
        - no arguments: Apply heuristic for all graph.
        - a node: Applies heuristic on that node only.
        - a list of nodes: Applies heuristic on all nodes of the list."""
        if nodes is None:
            return nx.all_pairs_shortest_path_length(self.g, self.depth)
            for f, dst in pairs.items():
                for t, _ in dst.items():
                    yield((f,t))
        else:
            if not isinstance(nodes, list):
                nodes = [nodes]
            for node in nodes:
                dests = nx.single_source_shortest_path_length(self.g, node, self.depth)
                for k in dests:
                    yield((node, k))
