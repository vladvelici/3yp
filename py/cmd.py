#!/usr/local/bin/python3

import sim
import provider as pr
import sys
import argparse
import tarfile
import simcache
import math
import random
import evalf

def main():
    parser = argparse.ArgumentParser()

    sbp = parser.add_subparsers(dest="action", help="Action to run.")

    p_train = sbp.add_parser("train", help="Train a similarity index.")
    p_train.add_argument("input", help="Path to input file.")
    p_train.add_argument("--format", "-f", default="csv",
                            choices=["csv"],
                            help="Input file format.")
    p_train.add_argument("--output", "-o", help="Output path for matrices q,z.",
                            required=True)
    p_train.add_argument("--eigenvalues", "-k", help="Number of eigenvalues to use",
                            default=6, dest="k", type=int)
    p_train.add_argument("--penalise", "-mu", help="Penalisation factor",
                            default=0.5, dest="mu", type=float)
    p_train.add_argument("--long", help="Don't use Cholesky decomposition.", action="store_true")
    p_train.add_argument("--direct", "-d", help="Use the input values as int node ids.",
                            action="store_true")
    p_train.add_argument("--offset", default=0, type=int,
        help="Offset for node ids in direct mode. Set to -1 for Matlab compatibility")

    p_info = sbp.add_parser("info", help="Get info about an index file.")
    p_info.add_argument("index", help="Path to index file.")
    p_info.add_argument("--nodes", help="Show all nodes", action="store_true")
    p_info.add_argument("-q", help="Print matrix Q.", action="store_true")
    p_info.add_argument("-z", help="Print matriz Z.", action="store_true")

    p_sim = sbp.add_parser("sim", help="Compute similarity between given edges.")
    p_sim.add_argument("index", help="Similartiy index saved by train.")
    p_sim.add_argument("nodes", help="Node(s) from which to compute similarity.",
                            nargs='*')
    p_sim.add_argument("--to", "-t", help="Node(s) to which to compute similarity.",
                            nargs='*')
    p_sim.add_argument("--top", help="Compute top similar nodes, sort by similarity.",
                            type=int, default=0)

    p_eval = sbp.add_parser("eval", help="Evaluate index using a list of (should predict) edges.")
    p_eval.add_argument("index", help="Index or graph file.")
    p_eval.add_argument("edges", help="Edges file.")
    p_eval.add_argument("--format", "-f", default="csv", choices=["csv"], help="Edges file format.")
    p_eval.add_argument("--offset", type=int, default=0, help="Nodes will be considered ints and added offset to ids.")
    p_eval.add_argument("--cache", action="store_true", help="Use an undirected cache. Undirected graphs only.")

    args = parser.parse_args()
    if args.action == 'sim':
        similarity(args)
    elif args.action == 'train':
        train(args)
    elif args.action == 'info':
        info(args)
    elif args.action == 'eval':
        evaluate(args)

### TRAIN

def train(args):
    """Perform training from a graph file. Use the values provided."""

    edgelist = []
    if args.format == 'csv':
        edgelist = pr.csv_file(args.input)

    s = None
    if not args.direct:
        prov = pr.EdgeList(edgelist=edgelist)
        print("Length of provider: %d" % len(prov))
        s = sim.trainp(prov, args.mu, args.k, args.long)
    else:
        adj = pr.mkadj(edgelist, args.offset)
        s = sim.train(adj, args.mu, args.k, args.long)

    s.save(args.output)

### SIMILARITY

def read_index(path):
    if tarfile.is_tarfile(path):
        return sim.loadp(path)
    else:
        return sim.load(path)

def similarity(args):
    s = read_index(args.index)

    nodes = args.nodes
    if len(nodes) == 0:
        nodes = s.nodelist()

    if args.top <= 0:
        to = args.to
        if to is None:
            to = s.nodelist()
        for a in nodes:
            for b in to:
                score = s.score(a,b)
                print("%s\t%s\t%e" % (a,b,score))
    else:
        all_nodes = s.nodelist()
        for node in nodes:
            top = []
            for b in all_nodes:
                if str(b) == str(node):
                    continue
                score = s.score(node,b)
                top.append((b, score))
            top = sorted(top, key=lambda it: it[1])
            top = top[:args.top]
            print(node, end="")
            print("\t", end="")
            for t in top:
                print("(%s, %e)" % t, end="\t")
            print()

### EVALUATE

def evaluate(args):
    index = read_index(args.index)

    edges = []
    if args.format == 'csv':
        edges = pr.csv_file(args.edges)

    def show_progress(edge, position, score, relative_score, i):
        progress = (i+1.0)*100/len(edges)
        print("\r%.2f %%" % progress, end="       ")

    res = evalf.evaluate(
        index=index,
        edges=edges,
        cache=args.cache,
        offset=args.offset,
        eachFunc=show_progress
    )

    print(end="\r")
    print("Top position offset:\t %e" % res.position)
    print("Total score:\t\t %e" % res.score)
    print("Total relative score:\t %e" % res.relative)
    print("")

    print("Rand Top position offset:\t %e" % res.rand_position)
    print("Rand Total score:\t\t %e" % res.rand_score)
    print("Rand Total relative score:\t %e" % res.rand_relative)

    print("")
    print("Differences (random - expected)")
    print("top position offset:\t %e" % res.diff_position)
    print("Total score:\t\t %e" % res.diff_score)
    print("Total relative score:\t %e" % res.diff_relative)
    print("\nEdges to predict:\t%d\nNo of nodes:\t%d." % (res.edges, res.nodes))


### INFO

def info(args):
    if tarfile.is_tarfile(args.index):
        info_tar(args)
    else:
        info_sim(args)

def info_sim(args):
    s = None
    try:
        s = sim.load(args.index)
    except:
        print("Cannot read index (plain) file.")
        return None

    print("Normal (plain q, z) index file with %d nodes." % len(s))
    print("Node names range from 0 to %d." % (len(s)-1))
    if s.z is None:
        print("Index is in short format (for Q=L^T*L, stores L^T * Z^T).")
    else:
        print("Index in in long format (stores both Q and Z).")
    if args.q:
        print("")
        print("Matrix Q:")
        print(s.q)
    if args.z:
        print("")
        print("Matriz Z:")
        print(s.z)

def info_tar(args):
    s = None
    try:
        s = sim.loadp(args.index)
    except:
        print("Cannot read index (tar) file.")
        return None

    print("tar index file with %s nodes." % len(s.provider))
    if s.z is None:
        print("Index is in short format (for Q=L^T*L, stores L^T * Z^T).")
    else:
        print("Index in in long format (stores both Q and Z).")
    print("")
    if args.q:
        print("Matrix Q:")
        print(s.q)
        print("")
    if args.z and s.z is not None:
        print("Matriz Z:")
        print(s.z)
        print("")

    nl = s.provider.nodelist()
    if args.nodes:
        print("All nodes:")
    else:
        print("A few nodes:")
        nl = nl[:5]
    print("\nid\tname")
    for index, node in enumerate(nl):
        print("%d\t%s" % (index, node))
    print()

if __name__ == '__main__':
    main()
