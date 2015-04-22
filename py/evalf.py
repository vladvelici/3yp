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
    'good_position',
    'better_than_random',
    'rand_position',
    'rand_good_position',
    'score',
    'rand_score',
    'relative',
    'rand_relative',
    'diff_position',
    'diff_score',
    'diff_relative'])

def _train_and_eval(prov, mu, k, edges, cache, eachFunc, trainfunc, heu, blacklist, picks):
    index = trainfunc(prov, mu, k)

    if eachFunc is None:
        def show_progress(edge, position, score, relative_score, i):
            progress = (i+1.0)*100/len(edges)
            print("\r%.2f %%\t for k=%d mu=%f" % (progress, k, mu), end="         ")

        eachFunc = show_progress

    return evaluate(
        index=index,
        edges=edges,
        cache=cache,
        eachFunc=eachFunc,
        heu=heu,
        blacklist=blacklist,
        picks=picks,
    )

# direct=true for any numeric offset. Set to None for direct=false
def train_and_evaluate(input, offset, range_mu, range_k, edges, cache, eachFunc=None, directed="auto", heu=None):
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

    blacklist = Blacklist(input).add(edges)

    picks = None
#    for a, _ in edges:
#        picks[a] = [i for i in prov.nodelist() if (a,i) not in blacklist]

    res = []
    for mu in range_mu:
        for k in range_k:
            res.append((mu, k, _train_and_eval(prov, mu, k, edges, cache, eachFunc, trainfunc, heu, blacklist, picks)))
    return res

class Blacklist:
    def __init__(self, edges):
        self._d = frozenset(edges)

    def add(self, edges):
        self._d = self._d.union(edges)

    def __contains__(self, pair):
        return pair[0] == pair[1] or str(pair[0]) == str(pair[1]) or pair in self._d or (str(pair[0]), str(pair[1])) in self._d

def evaluate(index, edges, cache, eachFunc=None, heu=None, blacklist=None, picks=None):
    sc = simcache.apply(index, cache)

    if blacklist is None:
        blacklist = Blacklist(edges)

    total_position = 0.0
    total_score = 0.0
    total_relative_score = 0.0
    good_position = 0
    better_than_random = 0

    rand_total_position = 0.0
    rand_good_position = 0
    rand_total_score = 0.0
    rand_total_relative_score = 0.0

    good_threshold = 5

    allnodes = index.nodelist()
    for i, pair in enumerate(edges):
        a = pair[0]
        targetb = pair[1]

        # dangeours-ish code
        if picks is None:
            randomtarget = random.sample(allnodes, 1)[0]
            thenumber = 0
            while (a, randomtarget) in blacklist:
                randomtarget = random.sample(allnodes, 1)[0]
                thenumber = thenumber + 1
            if thenumber > 2:
                print("Spent %d loops for random." % thenumber)
        else:
            randomtarget = random.sample(picks[a], 1)[0]

        position = 1
        rand_pos = 1
        score = sc.score(a,targetb)
        rand_score = sc.score(a,randomtarget)
        best = score

        enum = None
        if heu is not None:
            enum = heu(a)
        else:
            enum = allnodes

        for b in enum:
            if (a,b) in blacklist:
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

        if score < rand_score:
            better_than_random = better_than_random + 1

        total_position = total_position + position
        if position <= good_threshold:
            good_position = good_position + 1

        total_score = total_score + score
        total_relative_score = total_relative_score + relative_score

        rand_total_position = rand_total_position + rand_pos
        if rand_pos <= good_threshold:
            rand_good_position = rand_good_position + 1
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
        nodes               =       no_nodes,
        edges               =       len(edges),
        position            =       total_position,
        good_position       =       good_position,
        rand_position       =       rand_total_position,
        score               =       total_score,
        better_than_random  =       better_than_random,
        rand_score          =       rand_total_score,
        relative            =       total_relative_score,
        rand_relative       =       rand_total_relative_score,
        rand_good_position  =       rand_good_position,
        diff_position       =       rand_total_position - total_position,
        diff_score          =       rand_total_score - total_score,
        diff_relative       =       rand_total_relative_score - total_relative_score
    )
