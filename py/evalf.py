import provider as pr
import sim
import tarfile
from collections import namedtuple
import random
import simcache

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
    index = trainfunc(prov, mu, k)

    if eachFunc is None:
        def show_progress(edge, position, score, relative_score, i):
            progress = (i+1.0)*100/len(edges)
            print("\r%.2f %%\t for k=%d mu=%f" % (progress, k, mu), end="         ")

        eachFunc = show_progress

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
        prov = pr.Offset(input, offset)

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
        sc = simcache.precomputeSkip(index)
    else:
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

        enum = None
        if heu is not None:
            enum = heu(a)
        else:
            enum = enumerate(allnodes)

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

        if i % 100 == 0 and eachFunc is not None:
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
