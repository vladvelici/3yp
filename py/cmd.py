#!/usr/local/bin/python3

import sim
import provider as pr
import sys
import argparse
import tarfile
import math
import random
import evalf
import heuristics
import simcache
import numpy as np
import drawing

cache_options = simcache.OPTIONS

def main():
    """Intro point into the command line tool. Process command line arguments
    and delegate to the relevant function."""

    parser = argparse.ArgumentParser()

    sbp = parser.add_subparsers(dest="action", help="Action to run.")

    ## TRAIN
    p_train = sbp.add_parser("train", help="Train a similarity index.")
    p_train.add_argument("input", help="Path to input graph.")
    p_train.add_argument("--format", "-f", default="csv",
                            choices=["csv"],
                            help="Input graph file format.")
    p_train.add_argument("--type", "-t", help="Type of the graph. a for autodetect.",
                            default="auto", choices=["a", "auto", "d", "directed", "u", "undirected"])
    p_train.add_argument("--output", "-o", help="Output path for index file.",
                            required=True)
    p_train.add_argument("--eigenvalues", "-k", help="Number of eigenvalues to use. Must be less then no. of nodes.",
                            default=6, dest="k", type=int)
    p_train.add_argument("--penalise", "-mu", help="Penalising factor, must be between 0 and 1.",
                            default=0.5, dest="mu", type=float)
    p_train.add_argument("--long", help="Don't use Cholesky decomposition for undirected graphs.", action="store_true")
    p_train.add_argument("--direct", "-d", help="Use the input vertex IDs as integers directly.",
                            action="store_true")
    p_train.add_argument("--offset", default=0, type=int,
        help="Offset for vertex IDs in direct mode. Set to -1 for Matlab compatibility.")

    ## ACTION
    p_info = sbp.add_parser("info", help="Get info about an index file.")
    p_info.add_argument("index", help="Path to index file.")
    p_info.add_argument("--nodes", help="Show all nodes", action="store_true")
    p_info.add_argument("-q", help="Print matrix Q.", action="store_true")
    p_info.add_argument("-z", help="Print matriz Z (some index files do not have a Z).", action="store_true")

    ## SIMILARITY
    p_sim = sbp.add_parser("sim", help="Compute similarity between given edges.")
    p_sim.add_argument("index", help="Similartiy index (as saved by train).")
    p_sim.add_argument("nodes", help="Node(s) from which to compute similarity.",
                            nargs='*')
    p_sim.add_argument("--to", "-t", help="Node(s) to which to compute similarity.",
                            nargs='*')
    p_sim.add_argument("--top", help="Compute top similar nodes, sort by similarity.",
                            type=int, default=0)

    ## TOP
    p_top = sbp.add_parser("top", help="Compute top similar vertices for given vertices. More advanced then `sim --top`.")
    p_top.add_argument("index", help="Similarity index (as saved by train).")
    p_top.add_argument("nodes", help="Vertices from which to compute similarity.", nargs="*")
    p_top.add_argument("--limit", "-l", help="Limit the number of total results", type=int, default=0)
    p_top.add_argument("--graph", "-g", help="Graph file to use with maxdepth heuristic. CSV format.")
    p_top.add_argument("--depth", "-d", help="The depth for the heuristic function", default=3)
    p_top.add_argument("--blacklist", "-b", help="Blacklist graph file.", default=None)
    p_top.add_argument("--cache", help="Type of cache to use.", choices=cache_options, default=simcache.SCORE)

    ## MAKE DOT FILE WITH TOP
    p_dot = sbp.add_parser("dot", help="Create a dot file.")
    p_dot.add_argument("index", help="Similarity index saved by train.")
    p_dot.add_argument("graph", help="Graph to use.")
    p_dot.add_argument("--limit", "-l", help="Limit the number of total results", type=int, default=10)
    p_dot.add_argument("--depth", "-d", help="The depth for the heuristic function", default=3, type=int)
    p_dot.add_argument("--cache", help="Type of cache to use.", choices=cache_options, default=simcache.SCORE)
    
    # MAKE DOT FRAME
    p_dotf = sbp.add_parser("dotframe", help="Create a dot file for a frame of brute-force computation.")
    p_dotf.add_argument("graph", help="Graph to use. Assume direct format with offset 0.")
    p_dotf.add_argument("node", help="ID of node to use.", type=int)
    p_dotf.add_argument("output", help="Output file name")

    p_dotf.add_argument("--eigenvalues", "-k", help="Number of iterations in brute-force mode.",
                            default=6, dest="k", type=int)
    p_dotf.add_argument("--penalise", "-mu", help="Penalising factor, must be between 0 and 1.",
                            default=0.5, dest="mu", type=float)

    ## EVALUATION
    p_eval = sbp.add_parser("eval", help="Evaluate index using a list of (should predict) edges.")
    p_eval.add_argument("index", help="Index file.")
    p_eval.add_argument("edges", help="Edges file.")
    p_eval.add_argument("--format", "-f", default="csv", choices=["csv"], help="Edges file format.")
    p_eval.add_argument("--cache", help="Type of cache to use.", choices=cache_options, default=simcache.SCORE)
    p_eval.add_argument("--graph", "-g", help="Graph file to use with maxdepth heuristic. CSV format.")
    p_eval.add_argument("--depth", "-d", help="The depth for the heuristic function", default=3, type=int)

    ## TRAIN AND EVALUATE
    p_trev = sbp.add_parser("trev", help="Train and evaluate on a range of mu and k.")
    p_trev.add_argument("input", help="Graph file for training.")
    p_trev.add_argument("edges", help="Eval edges file.")
    p_trev.add_argument("--type", "-t", help="Type of the graph.",
                        default="auto", choices=["a", "auto", "d", "directed", "u", "undirected"])
    p_trev.add_argument("--format", "-f", help="Format for input file.", choices=["csv"], default='csv')
    p_trev.add_argument("--formatedge", help="Format for edges file.", choices=["csv"], default='csv')
    p_trev.add_argument("--offset", type=int, default=0, help="Offset to use, treat nodes are ints. Only works if --direct is set.")
    p_trev.add_argument("--direct", help="Assume nodes are ints. Assumes min(node_id+offset)=0.", action="store_true")
    p_trev.add_argument("--eigenvalues", "-k", help="List of k (no. of eigenvalues to use).",
                            nargs='+', type=int, dest="k")
    p_trev.add_argument("--penalise", "-mu", help="List of penalisation factors (mu).",
                        nargs='+', type=float, dest="mu")
    p_trev.add_argument("--depth", "-d", help="Depth for maxdepth heuristic.", type=int, default=0)
    p_trev.add_argument("--cache", help="Type of cache to use.", choices=cache_options, default=simcache.SCORE)

    args = parser.parse_args()
    if args.action == 'sim':
        similarity(args)
    elif args.action == 'train':
        train(args)
    elif args.action == 'info':
        info(args)
    elif args.action == 'eval':
        evaluate(args)
    elif args.action == 'trev':
        train_eval(args)
    elif args.action == 'top':
        top(args)
    elif args.action == 'dot':
        make_dot(args)
    elif args.action == "dotframe":
        make_dot_frames(args)

### TRAIN

def _train(args):
    """Train helper function. Reads input graph, creates the relevant provider
    object, trains an index using the relevant train function and returns the
    Sim object."""

    edgelist = []
    if args.format == 'csv':
        edgelist = pr.csv_file(args.input)
    else:
        print("Format not supported. :(")
        return

    prov = None
    if not args.direct:
        prov = pr.EdgeList(edgelist=edgelist)
        print("Length of EdgeList provider: %d" % len(prov))
    else:
        prov = pr.Offset(edgelist, args.offset)
        print("Using Offset provider.")

    s = None
    if args.type == "auto" or args.type == "a":
        s = sim.trainp(prov, args.mu, args.k, args.long)
    elif args.type == "directed" or args.type == "d":
        s = sim.trainp_directed(prov, args.mu, args.k, args.long)
    else:
        s = sim.trainp_undirected(prov, args.mu, args.k, args.long)

    return s

def train(args):
    """Perform training from a graph file using the given arguments. Save the
    index file."""
    s = _train(args)
    if s is not None:
        s.save(args.output)

### SIMILARITY

def read_index(path):
    """Helper function to read an index file. It returns a Sim or a Simp object,
    depending on the type of index.

    * tar index results in Simp object
    * plain index results in a Sim object
    """

    if tarfile.is_tarfile(path):
        return sim.loadp(path)
    else:
        return sim.load(path)

def similarity(args):
    """Computes the similarities between the given nodes using the given index
    file and prints them on the screen. Includes minimalistic top functionality.
    For better top computations, use **top**.
    """
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

### TOP

def fromToHeuristic(to):
    """A fake heuristic function that simply yields all the edges in the graph.
    It is used as a convenience function in some use cases (e.g. computing tops).

    It returns a function similar to heuristics.Maxdepth.top_gen, but it generates
    all possible edges using the to parameter, and the from parameter given to it.
    """
    def h(fr):
        for a in fr:
            for b in to:
                yield((a,b))
    return h

def top(args):
    """Computes the top pairs from an index file and prints them on standard
    output. It can be configured to use heuristics, different blacklists, and
    different limits."""
    s = read_index(args.index)
    s = simcache.apply(s, args.cache)
    heu = None
    if args.graph is not None and len(args.graph) > 0:
        edges = pr.csv_file(args.graph)
        edges = [(s.nid(x), s.nid(y)) for x,y in edges]
        h = heuristics.Maxdepth(edges, args.depth)
        heu = h.topGen
    else:
        heu = fromToHeuristic(s.nodelist())

    gen = None
    if len(args.nodes) > 0:
        gen = heu(args.nodes)
    else:
        gen = heu(s.nodelist())

    blacklist = None
    if args.blacklist is not None:
        be = pr.csv_file(args.blacklist)
        be = [(s.nid(x),s.nid(y)) for x,y in be]
        blacklist = evalf.Blacklist(be)

    top = []
    for edge in gen:
        if blacklist is not None and edge in blacklist:
            continue
        score = s.score(edge[0], edge[1])
        top.append((edge[0], edge[1], score))

    top = sorted(top, key=lambda it: it[2])
    if args.limit > 0:
        top = top[:args.limit]

    for entry in top:
        print("%s\t%s\t%e" % entry)

## MAKE DOT FILE

def make_dot(args):
    """It takes a graph and an index file and creates a dot file that can be
    used for visualisation using Graphviz. The number of top similar pairs to be
    rendered is configurable, as well as the heuristic. The backlist used is a
    set of the edges in the graph."""
    index = read_index(args.index)
    index = simcache.apply(index, args.cache)

    edges = pr.csv_file(args.graph)
    edges = [(index.nid(x), index.nid(y)) for x,y in edges]

    heu = None
    if args.depth > 0:
        h = heuristics.Maxdepth(edges, args.depth)
        heu = h.top
    else:
        heu = lambda x: index.nodelist()

    blacklist = evalf.Blacklist(edges)

    gtop = []
    args.limit = args.limit-1
    for a in index.nodelist():
        top = []
        for b in heu(a):
            if (a,b) in blacklist:
                continue
            if len(top) < args.limit:
                top.append((a,b,index.score(a,b)))
            elif len(top) == args.limit:
                top.append((a,b,index.score(a,b)))
                top = sorted(top, key=lambda it: it[2])
            else:
                score = index.score(a,b)
                p = len(top)-1
                if top[p][2] > score:
                    top[p] = (a,b,score)
                    p = p - 1
                    while p>0 and top[p][2] > score:
                        top[p], top[p-1] = top[p-1], top[p]
                        p=p-1
        gtop.append(top)

    print("strict graph {")
    print("  node[shape=point, label=\"\"];")
    print("  edge[color=\"#33333377\"];")
    for a,b in edges:
        print("  %s -- %s" % (a,b))
    for top in gtop:
        for pair in top:
            print("  %s -- %s [color=\"#ee333377\"]" % (str(pair[0]), str(pair[1])))
    print("}")


def make_dot_frames(args):
    """Direct computations only."""
    edges = pr.csv_file(args.graph)
    
    adj = pr.mkadj(edges)
    
    # normalize
    nadj = sim.normalise_adj(adj)
    ci = np.matrix(np.eye(adj.shape[0]))[:,args.node]

    for i in range(args.k):
        ci = ci + nadj[:,args.node] * args.mu
        nadj = nadj * nadj
        args.mu = args.mu*args.mu

    d = drawing.edgelist(edges) 
    d.add_properties(drawing.strength_color(ci.copy(), label=False))
#    d.add_properties(drawing.strength_size(ci.copy(), sf=lambda v: "4!" if v > 0 else "1!"))

    with open(args.output, "w") as f:
        dot_format = d.dot(f)

    with open(args.output, "w") as f:
        dot_format = d.dot(f)

def change_svg_file(args):


    edges = pr.csv_file(args.graph)
    
    adj = pr.mkadj(edges)
    
    # normalize
    nadj = sim.normalise_adj(adj)
    ci = np.matrix(np.eye(adj.shape[0]))[:,args.node]
    
    with open ("rendered.svg", "r") as myfile:
        layout=myfile.read()
        for i in range(args.k):

            # first frame here.

            ci = ci + nadj[:,args.node] * args.mu
            nadj = nadj * nadj
            args.mu = args.mu*args.mu
        

### TRAIN AND EVALUATE

def train_eval(args):
    """Take a graph and a test set, and train using a range of mu and k. Then
    performs a similar evaluation (to eval) for each combination of mu and k.
    The results are printed on standard output."""
    edgelist = []
    if args.format == 'csv':
        edgelist = pr.csv_file(args.input)
    else:
        print("Input format not supported. :(")
        return

    edges = []
    if args.formatedge == 'csv':
        edges = pr.csv_file(args.edges)
    else:
        print("Eval edges format not supported. :(")

    if not args.direct:
        args.offset = None

    heu = None
    if args.depth > 0:
        h = heuristics.Maxdepth(edgelist, args.depth)
        heu = h.top

    results = evalf.train_and_evaluate(
        input = edgelist,
        offset = args.offset,
        range_k = args.k,
        range_mu = args.mu,
        edges = edges,
        directed = args.type,
        cache = args.cache,
        heu = heu)

    print("\r")
    print("mu\tk\tposition\tgood pos\tscore   \trelative\tbetter rnd\tdiff pos\trnd gPos\trand scr\tdiff scr\tdiff rel")
    for res in results:
        r = res[2]
        print("%.2f\t%d\t%e\t%e\t%e\t%e\t%e\t%e\t%e\t%e\t%e\t%e" % (res[0], res[1],
            r.position, r.good_position, r.score, r.relative, r.better_than_random,
            r.diff_position, r.rand_good_position, r.rand_score, r.diff_score, r.diff_relative))



### EVALUATE

def evaluate(args):
    """Takes an index file and a test set and performs an evaluation, giving
    the following metrics:

    * average top position of test pairs
    * average score of test pairs
    * average relative score of test pairs
    * percentage of test pairs in top 1%% similar vertices
    * percentage better than random
    * random average top position
    * random average score
    * random average relative score
    * percentage of random pairs in top 1%% similar vertices
    """
    index = read_index(args.index)

    edges = []
    if args.format == 'csv':
        edges = pr.csv_file(args.edges)
    else:
        print("Format not supported. :(")

    def show_progress(edge, position, score, relative_score, i):
        progress = (i+1.0)*100/len(edges)
        print("\r%.2f %%" % progress, end="       ")

    heu = None
    if args.graph is not None:
        graphcsv = pr.csv_file(args.graph)
        h = heuristics.Maxdepth(graphcsv, args.depth)
        heu = h.top

    res = evalf.evaluate(
        index=index,
        edges=edges,
        cache=args.cache,
        eachFunc=show_progress,
        heu=heu
    )

    print(end="\r")
    print("Average top position:\t %e" % res.position)
    print("Average score:\t\t %e" % res.score)
    print("Average relative score:\t %e" % res.relative)
    print("%% of test set in top 1%%:\t %f" % res.good_position)

    print("")

    print("Rand average position:\t %e" % res.rand_position)
    print("Rand average score:\t\t %e" % res.rand_score)
    print("Rand average relative score:\t %e" % res.rand_relative)
    print("%% of random in top 1%%:\t %f" % res.rand_good_position)

    print("")

    print("Differences (random - expected)")
    print("Average top position:\t %e" % res.diff_position)
    print("Average score:\t\t %e" % res.diff_score)
    print("Average relative score:\t %e" % res.diff_relative)
    print("%% better than random:\t %f" % res.better_than_random)

    print("\nEdges to predict:\t%d\nNo of nodes:\t%d." % (res.edges, res.nodes))


### INFO

def info(args):
    """Print information about an index file. Delegate to relevant index file
    type."""
    if tarfile.is_tarfile(args.index):
        info_tar(args)
    else:
        info_sim(args)

def info_sim(args):
    """Print information about a direct index file (that does not have a
    provider.)"""
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
    """Print information about an index file that has a provider (thus stored
    as a tar file containing the provider and sim object)."""
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
