#!/usr/local/bin/python3

import networkx as nx
import argparse, csv

def write_graph(f, edgelist):
    if type(f) is str:
        with open(f, "w") as fb:
            write_graph(fb, edgelist)
    else:
        writer = csv.writer(f)

        writer.writerows(edgelist)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("nodes", help="Number of nodes", type=int)
    parser.add_argument("edges", help="Number of edges", type=int)
    parser.add_argument("output", help="Output CSV file name")
    parser.add_argument("--directed", "-d", action="store_true", help="If true, the graph generated is directed. Otherwise undirected.")

    args = parser.parse_args()

    g = nx.gnm_random_graph(args.nodes,args.edges,directed=args.directed)

    edgelist = g.edges()
    if not args.directed:
        others = []
        for a,b in edgelist:
            others.append((b,a))
        edgelist.extend(others)
    
    write_graph(args.output, edgelist)

if __name__ == '__main__':
    main()

