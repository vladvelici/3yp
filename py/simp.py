import sim

class Simp(sim.Sim):
    def __init__(self, q, z, provider):
        self.q = s.q
        self.z = s.z
        self.provider = provider

    def sim(self, a, b):
        return sim.Sim.sim(self.provider.node(a), self.provider.node(b))

def prov(s, provider):
    """Promotes the given sim.Sim (s) to simp.Simp using the provider."""
    s.provider = provider
    s.__class__ = simp
    return s

def train(provider, mu, k):
    adj = provider.adj()
    return prov(sim.train(adj, mu, k), provider)

def load(path, provider):
    return prov(sim.load(path), provider)
