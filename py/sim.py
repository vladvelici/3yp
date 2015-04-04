import numpy as np
import scipy.sparse as sparse
import scipy.sparse.linalg as linalg
from scipy.linalg import cholesky
import tarfile
import tempfile
import provider

COMPLEX_TOLERANCE = 1e15

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
        res = pm[0,0]
        if np.iscomplex(res):
            if abs(res.imag) < COMPLEX_TOLERANCE:
                return res.real
            else:
                return res # this should not happen. complex and big.
        return np.real(res).tolist() # python hackery. complex type but real no.

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

def train_undirected(adj, mu, k, qandz=False):
    """Train for undirected graphs. Same as train(...) but without the extra check."""
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

def train_directed(adj, mu, k, qandz=False):
    """Train for directed graphs. Same as train(...) but without the extra check.
    For directed graphs, the number of eigenvalues used might be changed. This is due
    to getting complex numbers.

    If a complex eigenvalue, v, is found, then the algorithm makes sure that v* (the
    complex conjugate of v) is also computed and used. As there will only be two calls
    to scipy.sparse.linalg.eigs(), one for left and one for right eigenvectors, all
    the complex eigenvalues for which the complex conjugate is missing will simply be
    discarded. This usually means that at most one eigenvalue is discarded but it is
    not guaranteed.
    """
    val, vec = linalg.eigs(adj, k=k, which="LM")

    # check for complex conjugates
    i=0
    keep=[]
    while i<len(val):
        if val[i].imag == 0:
            keep.append(i)
        elif i != len(val)-1 and val[i+1].conj() == val[i]:
            keep.append(i)
            keep.append(i+1)
        i+=1

    val = val[keep]
    vec = vec[:,keep]
    vec = np.matrix(vec)

    # do the cleanup, assuming the same order (need to double-check on that)
    vall, vecl = linalg.eigs(adj.T, k=k, which="LM")
    vecl = vecl[:, keep]
    vecl = np.matrix(vecl)

    z = vecl * sparse.diags((1 / (1 - (mu * val))), 0)
    z = np.matrix(z)

    if qandz:
        return Sim(vec.T * vec, z)
    
    print("sim.train_directed: Directed decomposition not implemented. Using long version.")
    return Sim(vec.T * vec, z)

def is_symmetric(adj):
    e = adj.nonzero()
    for i in range(len(e[0])):
        if adj[e[0][i], e[1][i]] != adj[e[1][i], e[0][i]]:
            return False
    return True

def train(adj, mu, k, qandz=False):
    """Training for undirected graphs (symmetric adjacency matrix).

    Use the adjacency matrix to compute similarity matrices.
    It computes matrix Q and Z if the last argument is set to true. Default is
    false.

    If qandz is set to False (the default), it computes the matrix W using
    Cholesky decomposition. This will speed up pairwise comparisons but may or
    may not lose some precision.

    This function, before training, is checking whether the graph is undirected or directed
    by checking if the adj matrix is symmetric or not. (symmetric adjacency matrix means
    undirected graph).

    For speed, consider directly using the functions train_directed and train_undirected.

    It returns a Sim object.
    """

    if is_symmetric(adj):
        return train_undirected(adj, mu, k, qandz)
    return train_directed(adj, mu, k, qandz)



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

def scoremat(s):
    """Return the matrix of scores of all possible nodes.
    This function was written for testing purposes only."""
    m = []
    for i in s.nodelist():
        row = []
        for j in s.nodelist():
            row.append(s.score(i,j))
        m.append(row)
    return np.array(m)
