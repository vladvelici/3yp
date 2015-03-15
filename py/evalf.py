import provider as pr
import sim
import tarfile
from collections import namedtuple
import random

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

def evaluate(index, edges, cache, offset, eachFunc=None):
    sc = index
    if cache:
        sc = simcache.Undirected(index)

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

        if not offset == 0:
            a = int(a) + offset
            targetb = int(targetb) + offset

        # dangeours-ish code
        randomtarget = random.sample(allnodes, 1)[0]
        while str(randomtarget) == str(a):
            randomtarget = random.sample(allnodes, 1)[0]

        position = 0
        rand_pos = 0
        score = sc.score(a,targetb)
        rand_score = sc.score(a,randomtarget)
        best = score

        for b in allnodes:
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
