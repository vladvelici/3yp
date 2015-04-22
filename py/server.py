#!/usr/local/bin/python3

import sim
import provider as pr
import sys
import argparse
import tarfile
import simcache
import drawing
import app

def read_index(path):
    if tarfile.is_tarfile(path):
        return sim.loadp(path)
    else:
        return sim.load(path)


def main():
    index = None
    edges = None

    parser = argparse.ArgumentParser()

    parser.add_argument("graph", help="Graph CSV file to use.")
    parser.add_argument("index", help="Index file to use.", default=".")
    parser.add_argument("--offset", help="Offset to use, if any.", type=int,
                    default=9999999)
    parser.add_argument("--eigenvalues", "-k", help="Eigenvalues to use",
                    type=int, default=6, dest="k")
    parser.add_argument("--penalise", "-mu", help="Penalising factor",
                    type=float, default=0.5, dest="mu")
    args = parser.parse_args()

    edges = pr.csv_file(args.graph)

    if args.index == ".":
        prov = None
        if args.offset == 9999999:
            prov = pr.EdgeList(edgelist=edges)
        else:
            prov = pr.Offset(edges, args.offset)
        index = sim.trainp(prov, args.mu, args.k)
    else:
        index = read_index(args.index)

    app.init(index, edges, drawing.edgelist(edges))


if __name__ == "__main__":
    main()
