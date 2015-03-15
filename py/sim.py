import numpy as np
import scipy.sparse as sparse
import scipy.sparse.linalg as linalg
from scipy.linalg import cholesky
import tarfile
import tempfile
import provider

class Sim:
    def __init__(self, q, z=None):
        self.q = np.matrix(q)
        if z is None:
            self.z = None
        else:
            self.z = np.matrix(z)

    def __len__(self):
        """Returns the number of nodes provided in this method."""
        if self.z is None:
            return self.q.shape[1]
        return self.z.shape[0]

    def nodelist(self):
        return range(len(self))

    def _dotprod(self, a, b):
        a=int(a)
        b=int(b)
        pm = None
        if self.z is None:
            pm = self.q[:,a].T * self.q[:, b]
        else:
            pm = self.z[a,:] * self.q * self.z[b,:].transpose()
        return pm[0,0]

    def score(self, a, b):
        """Compute the score between a and b. The score is the eucliden
        distance between the similarity vectors of the nodes. (c_a and c_b)"""
        norma = self._dotprod(a,a)
        normb = self._dotprod(b,b)
        ab = self._dotprod(a,b)
        return norma + normb - 2 * ab

    def save(self, path):
        """Save Sim object to file."""
        if type(path) == str:
            with open(path, mode='wb') as f:
                self.save(f)
            return
        if self.z is None:
            np.savez(path, q=self.q)
        else:
            np.savez(path, q=self.q, z=self.z)

def train(adj, mu, k, qandz=False):
    """Training for undirected graphs (symmetric adjacency matrix).

    Use the adjacency matrix to compute similarity matrices.
    It computes matrix Q and Z if the last argument is set to true. Default is
    false.

    If qandz is set to False (the default), it computes the matrix W using
    Cholesky decomposition. This will speed up pairwise comparisons but may or
    may not lose some precision.

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

    if qandz:
        return Sim(q, z)

    q = cholesky(q, lower=True, overwrite_a=True, check_finite=False)
    q = np.matrix(q)
    omega = q.T * z.T
    return Sim(omega)

def load(path):
    """Load Sim object from file. It returns a Sim object."""
    if type(path) == str:
        with open(path, 'rb') as f:
            return load(f)
    else:
        data = np.load(path)
        if not 'q' in data:
            raise Exception("File doesn't have Q.")
        q = data['q']
        z = None
        if 'z' in data:
            z = data['z']
        return Sim(q,z)

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

def trainp(provider, mu, k, qandz=False):
    """Train with a provider instead of adjancency matrix."""
    adj = provider.adj()
    return prov(train(adj, mu, k, qandz), provider)

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
