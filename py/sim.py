import numpy as np
import scipy.sparse as sparse
import scipy.sparse.linalg as linalg

class Sim:
    def __init__(self, q, z):
        self.q = q
        self.z = z

    def __len__(self):
        """Returns the number of nodes provided in this method."""
        return self.z.shape[0]

    def score(self, a, b):
        """Compute the score between a and b."""
        norma = self.z[a,:] * self.q * self.z[a,:].transpose()
        normb = self.z[b,:] * self.q * self.z[b,:].transpose()
        ab = self.z[a,:] * self.q * self.z[b,:].transpose()
        return norma.item((0,0)) + normb.item((0,0)) - 2 * ab.item((0,0))

    def save(self, path):
        """Save Sim object to file."""
        with open(path, mode='wb') as f:
            np.savez(f, q=self.q, z=self.z)

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

def load(path):
    """Load Sim object from file."""
    with open(path, 'rb') as f:
        data = np.load(f)
        if not('q' in data and 'z' in data):
            raise Exception("File doesn't have q and z.")
        return Sim(data['q'], data['z'])

## With provider

class Simp(Sim):
    def __init__(self, q, z, provider):
        self.q = s.q
        self.z = s.z
        self.provider = provider

    def score(self, a, b):
        return Sim.score(self, self.provider.node(a), self.provider.node(b))

def prov(s, provider):
    """Promotes the given Sim (s) to simp.Simp using the provider."""
    s.provider = provider
    s.__class__ = Simp
    return s

def trainp(provider, mu, k):
    """Train with a provider instead of adjancency matrix."""
    adj = provider.adj()
    return prov(train(adj, mu, k), provider)

def load(path, provider):
    """Load and prov convenience function."""
    return prov(load(path), provider)
