#!/usr/local/bin/python3

import sim
import provider as pr
import sys
import argparse
import tarfile
from scipy.sparse import csr_matrix

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("old", help="File to the old plain index.")
    parser.add_argument("new", help="Output file for the updated index.")
    parser.add_argument("offset", help="Offset number to use.", type=int, default=0)

    args = parser.parse_args()

    if tarfile.is_tarfile(args.old):
        print("The index has the new type. No action required.")
        return

    index = sim.load(args.old)

    prov = pr.Offset(None, args.offset)
    length = len(index)
    print("found len",length)
    prov._adj = csr_matrix((length, length))
    print(prov._adj.shape)

    newindex = sim.prov(index, prov)
    newindex.save(args.new)

if __name__ == '__main__':
    main()
