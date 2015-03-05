from scipy.sparse import coo_matrix
from scipy.sparse import csr_matrix

class Simple:
    """Reduntant adjacency matrix provider."""
    def __init__(self, adj):
        self.adj = adj

    def adj(self):
        """Returns the adjacency given at instantiation."""
        return self.adj

    def node(self, node):
        """Returns the node given."""
        return node


class EdgeList:
    """Reads a CSV file of edges in format:
    node_one, node_two[, ignored attributes]

    The node names from the csv files are treated as strings,
    and assigned unique consecutive numbers starting form 0.
    """

    _index = {}
    _nextId = 0
    _edgelist = None
    _adj = None

    def __init__(self, edgelist):
        self._edgelist = edgelist
        self._mkindex()

    def _mkindex(self):
        """Create a node index by iterating over all the edges."""
        for edge in self._edgelist:
            self.node(edge[0])
            self.node(edge[1])

    def _makeadj(self):
        pass

    def node(self, n):
        """Return an interger ID for node str."""
        if n in self._index:
            return self._index[n]
        self._index[n] = self._nextId
        r = self._nextId
        self._nextId = self._nextId+1
        return r

    def adj(self):
        """Get the adjacency matrix."""
        if self._adj is None:
            _makead()
        return self._adj
