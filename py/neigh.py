#!/usr/local/bin/python3

import provider as pr
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("graph", help="Graph to use")
    parser.add_argument("nodes", help="Nodes from which...", nargs="+")

    args = parser.parse_args()

    edges = pr.csv_file(args.graph)

    for i in args.nodes:
        print("=== For node %s ===" % str(i))
        
        lst = [(a,b) for a,b in edges if a == i]
        print("Edge count = %d" % len(lst))
        for b in lst:
            print(b)
    
if __name__ == '__main__':
    main()


