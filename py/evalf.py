import provider as pr
import sim
import tarfile
from collections import namedtuple
import random
import simcache

class Offset_provider:
    """Provider for offests and direct edgelists.
    Mostly used as a adj matrix cache.
    """

    def __init__(edgelist, offset):
        self.offset = offset
        self._adj = pr.mkadj(edgelist, offset)

    def __len__(self):
        return len(self._adj.shape[0])

    def _node(self, n):
        """Return an interger ID for node. Just add offset to n."""
        return self.offset + int(n)

    def nodelist(self):
        return range(self.offset, len(self) + self.offset)

    ## No persistence required.
    ## Implement the provider description for sim.Simp:

    def __getitem__(self, node):
        """Return the ID for node. Raises an exception if the node is not
        found."""
        return self.offset + int(node)

    def adj(self):
        """Get the adjacency matrix."""
        return self._adj

def read_index(path):
    if tarfile.is_tarfile(path):
        return sim.loadp(path)
    else:
        return sim.load(path)

EvalResult = namedtuple("EvalResult", [
    'nodes',
    'edges',
    'position',
    'rand_position',
    'score',
    'rand_score',
    'relative',
    'rand_relative',
    'diff_position',
    'diff_score',
    'diff_relative'])

def _train_and_eval(prov, mu, k, edges, eachFunc, trainfunc, heu):
    index = trainfunc(prov, mu, k, True)

    return evaluate(
        index=index,
        edges=edges,
        cache=True,
        eachFunc=eachFunc,
        heu=heu
    )

# direct=true for any numeric offset. Set to None for direct=false
def train_and_evaluate(input, offset, range_mu, range_k, edges, eachFunc=None, directed="auto", heu=None):
    """Returns a list of (mu, k, EvalResult)"""

    prov = None
    if offset is None:
        prov = pr.EdgeList(edgelist=input)
    else:
        prov = Offset_provider(input, offset)
        for i, _ in enumerate(edges):
            edges[i][0] = int(edges[i][0]) + offset
            edges[i][1] = int(edges[i][1]) + offset

    trainfunc = None
    if directed == "d" or directed == "directed":
        trainfunc = sim.trainp_directed
    elif directed == "u" or directed == "undirected":
        trainfunc = sim.trainp_undirected
    elif sim.is_symmetric(prov.adj()):
        trainfunc = sim.trainp_undirected
    else:
        trainfunc = sim.trainp_directed

    if heu is not None:
        ## The heuristic will run every time giving the same results. Cache it.
        heudict = {}
        for pair in heu([i for i,_ in edges]):
            if not pair[0] in heudict:
                heudict[pair[0]] = [pair[1]]
            else:
                heudict[pair[0]].append(pair[1])
        def heuf(nodes):
            if not isinstance(nodes, list):
                nodes = [nodes]
            for f in nodes:
                for to in heudict[f]:
                    yield(f, to)
        heu = heuf

    res = []
    for mu in range_mu:
        for k in range_k:
            res.append((mu, k, _train_and_eval(prov, mu, k, edges, eachFunc, trainfunc, heu)))
    return res

def evaluate(index, edges, cache, eachFunc=None, heu=None):
    sc = index
    if cache:
        sc = simcache.undirected(index)

    total_position = 0.0
    total_score = 0.0
    total_relative_score = 0.0

    rand_total_position = 0.0
    rand_total_score = 0.0
    rand_total_relative_score = 0.0

    allnodes = index.nodelist()
    for i, pair in enumerate(edges):
        a = pair[0]
        targetb = pair[1]

        # dangeours-ish code
        randomtarget = random.sample(allnodes, 1)[0]
        while str(randomtarget) == str(a):
            randomtarget = random.sample(allnodes, 1)[0]

        position = 0
        rand_pos = 0
        score = sc.score(a,targetb)
        rand_score = sc.score(a,randomtarget)
        best = score

        enum = enumerate(allnodes)
        if heu is not None:
            enum = heu(a)

        for _, b in enum:
            if a == b or str(b) == str(a):
                continue
            scr = sc.score(a,b)
            if scr < score:
                position = position + 1
            if scr < rand_score:
                rand_pos = rand_pos + 1
            if scr < best:
                best = scr

        relative_score = (score - best) ** 2
        rand_relative = (rand_score - best) ** 2

        total_position = total_position + position
        total_score = total_score + score
        total_relative_score = total_relative_score + relative_score

        rand_total_position = rand_total_position + rand_pos
        rand_total_score = rand_total_score + rand_score
        rand_total_relative_score = rand_total_relative_score + rand_relative

        if eachFunc is not None:
            eachFunc((a, targetb), position, score, relative_score, i)

    no_nodes = len(allnodes)
    total_position = total_position / (no_nodes*len(edges))
    total_score = total_score / len(edges)
    total_relative_score = total_relative_score / len(edges)

    rand_total_position = rand_total_position / (no_nodes * len(edges))
    rand_total_score = rand_total_score / len(edges)
    rand_total_relative_score = rand_total_relative_score / len(edges)

    return EvalResult(
        nodes=no_nodes,
        edges=len(edges),
        position=total_position,
        rand_position=rand_total_position,
        score=total_score,
        rand_score=rand_total_score,
        relative=total_relative_score,
        rand_relative=rand_total_relative_score,
        diff_position=rand_total_position-total_position,
        diff_score=rand_total_score-total_score,
        diff_relative=rand_total_relative_score-total_relative_score
    )
