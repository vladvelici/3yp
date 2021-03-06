from scipy.sparse import coo_matrix
from scipy.sparse import csr_matrix
import numpy as np
import csv, sys, pickle

def mkadj(edgelist, offset=0):
    """Return an adjacency matrix from a list of edges. There should be N nodes
    from 0 to N-1, and the format of edgelist is:

    [(1,2), (0,1), (2,1)] (meaning the directed edges 1->2, 0->1, 2->1)

    For an undirected graph, revert the pairs and append them at the end of the
    edge list.

    The offset is used to increase the compatibility with CSV files parsed for Matlab.
    It is added to the node id in the edgelist before using that ID. For compatibility
    with Matlab, use an offest of -1 (in Matlab, indices start at 1, not 0).

    Returns a sparse adjacency matrix of type csr_matrix.
    """
    rows = [0] * len(edgelist)
    cols = [0] * len(edgelist)

    maxNode = -1

    for i, edge in enumerate(edgelist):
        rows[i] = int(edge[0]) + offset
        cols[i] = int(edge[1]) + offset

        if maxNode < rows[i]:
            maxNode = rows[i]
        if maxNode < cols[i]:
            maxNode = cols[i]

    adj = coo_matrix((np.ones(len(rows)), (rows, cols)),
        shape=(maxNode+1, maxNode+1), dtype=float)

    return csr_matrix(adj)

class EdgeList:
    """Instantiated by a list of edges. Usually from CSV files.

    The node names from the csv files are treated as strings,
    and assigned unique consecutive numbers starting form 0.
    """

    def __init__(self, **args):
        """
        Accepted arguments:
            edgelist = list of edges (can be empty if not requred to compute
                       adjacency matrix [e.g. to train])
            invindex = inverted index of nodes (can be empty if edgelist provided)

        The inverted index needed is an array of nodes, where the first node
        has ID 0, the second one has ID 1, etc.

        The node->id index is computed using the given inverted index.
        """
        if "edgelist" in args:
            self._edgelist = args['edgelist']
        else:
            self._edgelist = []

        self._adj = None

        self._index = {}
        if "invindex" in args:
            self._inverted_index = args["invindex"]
            ## Compute the normal node->id index
            for intid, name in enumerate(args["invindex"]):
                self._index[name] = intid
        else:
            self._inverted_index = []
            self._mkindex()

    def __len__(self):
        return len(self._inverted_index)

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
        r = len(self._inverted_index)
        self._index[n] = r
        self._inverted_index.append(n)
        return r

    def nodelist(self):
        """Returns the list of vertices, in their original form."""
        return self._inverted_index

    ## Inverted index lookup:
    def inverted(self, id):
        """Given self[node]=id, then self.inverted(id)=node."""
        return self._inverted_index[id]

    ## Persistence:

    def save(self, where):
        """EdgeList is not saved. It should (already) be persisted somewhere."""
        if type(where) == str:
            with open(where, "wb") as f:
                pickle.dump(self._inverted_index, f)
        else:
            pickle.dump(self._inverted_index, where)

    ## Implement the provider description for sim.Simp:

    def __getitem__(self, node):
        """Return the ID for node. Raises an exception if the node is not
        found."""
        return self._index[node]

    def adj(self):
        """Get the adjacency matrix."""
        if self._adj is None:
            self._makeadj()
        return self._adj


class Offset:
    """Provider for offests and direct edgelists.
    Mostly used as a adj matrix cache.
    """

    def __init__(self, edgelist, offset):
        self.offset = offset
        if edgelist is not None:
            self._adj = mkadj(edgelist, offset)

    def __len__(self):
        return self._adj.shape[0]

    def nodelist(self):
        """Returns the list of vertices in their original form."""
        return range(-self.offset, len(self) - self.offset)

    def save(self, where):
        """EdgeList is not saved. It should (already) be persisted somewhere."""
        if type(where) == str:
            with open(where, "wb") as f:
                self.save(f)
        else:
            pickle.dump({
                "type": "offset",
                "offset": self.offset,
                "length": len(self)
            }, where)

    ## Inverted index lookup (might not be required, but for completeness)
    def inverted(self, node):
        return int(node) - self.offset

    ## Implement the provider description for sim.Simp:

    def __getitem__(self, node):
        """Return the ID for node. Raises an exception if the node is not
        found."""
        v = int(node) + self.offset
        if v < 0 or v >= len(self):
            raise KeyError("node[%s]+offset[%d]=%d is out of bounds." % (node, self.offset, v))
        return v

    def adj(self):
        """Get the adjacency matrix."""
        return self._adj

def load(where):
    """This loads the index file for the double dictonary (node->id, id->node),
    but does not load the adjacency matrix or edge list. This means the EdgeList
    returned by this method is not usable to train new graphs but only to make
    adjacency matrices with it, or/and use as a provider."""
    if type(where) == str:
        with open(where, "rb") as f:
            load(f)
    else:
        found = pickle.load(where)
        # guessing the type.
        if isinstance(found, dict) and "type" in found and found["type"] == "offset":
            o = Offset(None, found["offset"])
            o._adj = csr_matrix((found["length"], found["length"])) # fake empty adj
            return o
        else:
            return EdgeList(invindex=found)


def csv_stream(stream):
    """Reads a CSV stream to a list of edges (not EdgeList object).

    Use EdgeList(csv_stream(stream)) to obtain an EdgeList object.
    """
    reader = csv.reader(stream)
    res = []
    for row in reader:
        if len(row) < 2:
            raise Exception("Parsing CSV: Too few values in the row.", row, len(row))
        res.append((row[0].strip(), row[1].strip()))
    return res

def csv_file(path):
    """Convenience method to obtain an edge list from a CSV file path.

    Use EdgeList(csv_file(path)) to get an EdgeList object."""
    with open(path, newline='') as f:
        return csv_stream(f)
