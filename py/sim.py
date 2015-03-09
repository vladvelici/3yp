import numpy as np
import scipy.sparse as sparse
import scipy.sparse.linalg as linalg
import tarfile
import tempfile
import provider

class Sim:
    def __init__(self, q, z):
        self.q = np.matrix(q)
        self.z = np.matrix(z)

    def __len__(self):
        """Returns the number of nodes provided in this method."""
        return self.z.shape[0]

    def nodelist(self):
        return range(len(self))

    def score(self, a, b):
        """Compute the score between a and b. The score is the eucliden
        distance between the similarity vectors of the nodes. (c_a and c_b)"""
        norma = self.z[a,:] * self.q * self.z[a,:].transpose()
        normb = self.z[b,:] * self.q * self.z[b,:].transpose()
        ab = self.z[a,:] * self.q * self.z[b,:].transpose()
        return norma.item((0,0)) + normb.item((0,0)) - 2 * ab.item((0,0))

    def save(self, path):
        """Save Sim object to file."""
        if type(path) == str:
            with open(path, mode='wb') as f:
                np.savez(f, q=self.q, z=self.z)
        else:
            np.savez(path, q=self.q, z=self.z)

def train(adj, mu, k):
    """Use the adjacency matrix to compute matrices Q and Z.

    It returns a Sim object.
    """
    neigh = adj.sum(1)
    neighInv = np.power(neigh, -1)

    w = sparse.diags(neighInv.transpose().tolist(), [0])
    wHalf = np.sqrt(w)

    A = wHalf * adj * wHalf

    val, vec = linalg.eigsh(A, k=k, which="LM")
    val = np.power(1-val*mu, -1)
    val = sparse.diags([val], [0])

    vec = np.matrix(vec)

    z = sparse.diags(np.sqrt(neigh).transpose().tolist(), [0]) * vec * val
    q = vec.transpose() * w * vec

    return Sim(q, z)

def _load(f):
    data = np.load(f)
    if not('q' in data and 'z' in data):
        raise Exception("File doesn't have q and z.")
    return Sim(data['q'], data['z'])

def load(path):
    """Load Sim object from file. It returns a Sim object."""
    if type(path) == str:
        with open(path, 'rb') as f:
            return _load(f)
    else:
        return _load(path)

## With provider

class Simp(Sim):
    """Extend the class Sim to accept a provider instead of directly an
    adjacency matrix.

    The role of a provider is to create an adjacency matrix and have a mapping
    from nodes in the original (meaningful) format (e.g. strings or nodes in
    an actual graph) to nonnegative integers (representing the row or col index
    of the node in the adjacency matrix).

    provider.adj() -> returns a scipy.sparse (preferably csr) symmetric matrix.
    provider[meaningful_node_id] -> returns an unique numeric id for the node.
    provider.nodelist() -> gives a list of nodes (meaningful names)

    """
    def __init__(self, q, z, provider):
        self.q = np.matrix(s.q)
        self.z = np.matrix(s.z)
        self.provider = provider

    def score(self, a, b):
        return Sim.score(self, self.provider[a], self.provider[b])

    def nodelist(self):
        return self.provider.nodelist()

    def _save(self, f):
        simf = tempfile.TemporaryFile()
        Sim.save(self, simf)
        simf_size = simf.tell()
        simf.seek(0)

        provf = tempfile.TemporaryFile()
        self.provider.save(provf)
        provf_size = provf.tell()
        provf.seek(0)

        with tarfile.open(None, 'w', f) as tf:
            simti = tarfile.TarInfo(name="simqz")
            simti.size = simf_size
            tf.addfile(tarinfo=simti, fileobj=simf)

            provti = tarfile.TarInfo(name="provindex")
            provti.size = provf_size
            tf.addfile(tarinfo=provti,fileobj=provf)

        provf.close()
        simf.close()

    def save(self, path):
        if type(path) == str:
            with open(path, "wb") as f:
                self._save(f)
        else:
            self._save(path)

def prov(s, provider):
    """Promotes the given Sim (s) to simp.Simp using the provider."""
    s.provider = provider
    s.__class__ = Simp
    return s

def trainp(provider, mu, k):
    """Train with a provider instead of adjancency matrix."""
    adj = provider.adj()
    return prov(train(adj, mu, k), provider)

def loadprov(path, provider):
    """Load and prov convenience function. Returns a Simp object using the
    Sim object loaded from path and the provider passed to this function."""
    return prov(load(path), provider)

def _loadp(f):
    with tarfile.open(None, 'r', f) as tf:
        f_prov = tf.extractfile("provindex")
        f_sim = tf.extractfile("simqz")
        obj_prov = provider.load(f_prov)
        return loadprov(f_sim, obj_prov)

def loadp(path):
    """Load tar file containing EdgeList provider and Sim matrices.

    Returns a Simp object with an EdgeList provider linked to it. Note that
    the train() method will not work as there is no edgelist stored (so cannot
    obtain the adjacency matrix)"""
    if type(path) == str:
        with open(path, "rb") as f:
            return _loadp(f)
    else:
        return _loadp(path)
