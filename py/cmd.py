#!/usr/local/bin/python3

import sim
import provider as pr
import sys
import argparse
import tarfile

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


    args = parser.parse_args()
    if args.action == 'sim':
        similarity(args)
    elif args.action == 'train':
        train(args)
    elif args.action == 'info':
        info(args)

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
        s = sim.trainp(prov, args.mu, args.k)
    else:
        adj = pr.mkadj(edgelist, args.offset)
        s = sim.train(adj, args.mu, args.k)

    print(type(s))
    print("%e" % s.score(0,1))

    s.save(args.output)

### SIMILARITY

def read_index(path):
    if tarfile.is_tarfile(path):
        return sim.loadp(path)
    else:
        return sim.load(path)

def similarity(args):
    s = read_index(args.index)

    print(type(s))
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
                if b == node:
                    continue
                score = s.score(node,b)
                top.append((b, score))
            top = sorted(top, key=lambda it: it[1])
            top = top[:args.top]
            print("TODO")

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
    print("")
    if args.q:
        print("Matrix Q:")
        print(s.q)
        print("")
    if args.z:
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
