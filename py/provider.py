from scipy.sparse import coo_matrix
from scipy.sparse import csr_matrix
import numpy as np
import csv, sys

class Simple:
    """Reduntant adjacency matrix provider."""
    def __init__(self, adj):
        self.adj = adj

    def __len__(self):
        """Return the number of nodes."""
        return self.adj.shape[0]

    def __getitem__(self, key):
        """Assumes the key is the index in the adjacency matrix."""
        return key

    def adj(self):
        """Returns the adjacency given at instantiation."""
        return self.adj

class EdgeList:
    """Reads a CSV file of edges in format:
    node_one, node_two[, ignored attributes]

    The node names from the csv files are treated as strings,
    and assigned unique consecutive numbers starting form 0.
    """

    def __init__(self, edgelist):
        self._index = {}
        self._nextId = 0
        self._edgelist = edgelist
        self._adj = None
        self._mkindex()

    def __len__(self):
        return self._nextId

    def _mkindex(self):
        """Create a node index by iterating over all the edges."""
        for edge in self._edgelist:
            self._node(edge[0])
            self._node(edge[1])

    def _makeadj(self):
        """Create and save the adjacency matrix from the list of edges."""
        rows = [0] * len(self._edgelist)
        cols = [0] * len(self._edgelist)

        for i, edge in enumerate(self._edgelist):
            rows[i] = self[edge[0]]
            cols[i] = self[edge[1]]

        adj = coo_matrix((np.ones(len(rows)), (rows, cols)),
            shape=(len(self), len(self)), dtype=float)

        self._adj = csr_matrix(adj)

    def _node(self, n):
        """Return an interger ID for node str. Create a new ID if not already
        defined."""
        if n in self._index:
            return self._index[n]
        self._index[n] = self._nextId
        r = self._nextId
        self._nextId = self._nextId+1
        return r

    def __getitem__(self, node):
        """Return the ID for node. Raises an exception if the node is not
        found."""
        return self._index[node]

    def adj(self):
        """Get the adjacency matrix."""
        if self._adj is None:
            self._makeadj()
        return self._adj

def csv_stream(stream):
    """Reads a CSV stream to a list of edges (not EdgeList object).

    Use EdgeList(csv_stream(stream)) to obtain an EdgeList object.
    """
    reader = csv.reader(stream)
    res = []
    for row in reader:
        if len(row) < 2:
            raise Exception("Parsing CSV: Too few values in the row.", row, len(row))
        res.append((row[0], row[1]))
    return res

def csv_file(path):
    """Convenience method to obtain an edge list from a CSV file path.

    Use EdgeList(csv_file(path)) to get an EdgeList object."""
    with open(path, newline='') as f:
        return csv_stream(f)
