"""Drawing functions used with sigma.js implementations. It has helper methods
for outputting sigma.js friendly JSON and to manipulate it to colour the nodes
by their similarities (or other measures). Same for size.

It was used to draw Figure 1 in the final report.
"""

import json
import random
import numpy as np
import colorsys
from io import StringIO

def _anyprop(accepted, available):
    for i in accepted:
        if i in available:
            return True
    return False

class D:
    def __init__(self, sigma_dict):
        self.sigma_dict = sigma_dict

    def r(self):
        nodes = [node for _, node in self.sigma_dict["nodes"].items()]
        return {"edges": self.sigma_dict["edges"], "nodes": nodes}

    def json(self, dest=None):
        if dest is None:
            return json.dumps(self.r())
        elif type(dest) is str:
            with open(dest, "w") as f:
                return self.json(f)
        return json.dump(self.r(), dest)

    def dot(self, dest=None, directed=False):
        if dest is None:
            buf = StringIO()
        else:
            buf=dest

        if directed:
            buf.write("digraph {\n")
        else:
            buf.write("strict graph {\n")
        buf.write("  node[shape=circle style=filled fontcolor=white]\n")

        node_properties = ["label", "size", "color"]
        # write nodes
        for nid, props in self.sigma_dict["nodes"].items():
            buf.write("  " + nid)
            if _anyprop(node_properties, props):
                buf.write(" [")
                for acc in node_properties:
                    if acc in props:
                        buf.write(str(acc) + "=\"" + str(props[acc]) + "\" ")
                buf.write("]")
            buf.write("\n")

        # write edges
        write_edge = lambda x: x["source"] + " -- " + x["target"]
        if directed:
            write_edge = lambda x: x["source"] + "->" + x["target"]

        edge_properties = ["color", "label"]
        for edge in self.sigma_dict["edges"]:
            buf.write("  " + write_edge(edge))
            # properties:
            if _anyprop(edge_properties, edge):
                buf.write(" [")
                for acc in edge_properties:
                    if acc in edge:
                        buf.write(acc + "=\"" + edge[acc] + "\" ")
                buf.write("]")
            buf.write("\n")

        buf.write("}")
        return buf

    def add_properties(self, prop):
        for k,v in prop.items():
            # print(k,"\t",v)
            self.sigma_dict["nodes"][k].update(v)


def edgelist(edgelist):
    nodes = {}
    edges = []
    for edge in edgelist:
        a, b = edge[0], edge[1]
        if not a in nodes:
            nodes[a] = {"id": a, "label": a, "x": random.randint(0, 100), "y": random.randint(0, 100), "size": 2}
        if not b in nodes:
            nodes[b] = {"id": b, "label": b, "x": random.randint(0, 100), "y": random.randint(0, 100), "size": 2}
        edges.append({
            "id": str(a) + "_to_" + str(b),
            "source": a,
            "target": b,
            "color": "#cccccc"
        })

    return D({
        "nodes": nodes,
        "edges": edges
    })

def nonzero(arr):
    sources = arr[0]
    targets = arr[1]
    edges = []
    for i, src in enumerate(sources):
        edges.append((src, targets[i]))
    return edgelist(edges)

# Helper classes for strength_color:

class _id_dict:
    """Identity dictionary-like object."""
    def __getitem__(self, i):
        return i

class _tostr_dict:
    """Cast to string dictionary object."""
    def __getitem__(self, i):
        return str(i)

def strength_size(vector, ids=None, sf=None):
    """Change the size given the vector strength."""
    vector = vector / vector.max()
    res = {}
    if ids is None:
        ids = _tostr_dict()
    if sf is None:
        sf = lambda v: 5 if val > 0 else 4
    for index, val in enumerate(vector.flat):
        res[ids[index]] = {"size":  sf(val)}
    return res

def default_bcf(v):
    if v <= 0:
        return "#cccccc"
    r,g,b = colorsys.hls_to_rgb(0, 0.5, v);
    return "#%0.2X%0.2X%0.2X" % (int(round(r*255)), int(round(g*255)), int(round(b*255)))


def colour_vector(vector):
    vector = vector / vector.sum()
    values = np.unique(vector.flat)
    values = values[1:] if len(values) > 1 and values[0] == 0.0 else values
    colours = {0.0: 0.0}
    for index, val in enumerate(values):
        colours[val] = (index+1)/len(values)

    res = {}
    for index, val in enumerate(vector.flat):
        res[ids[index]] = {"color": bcf(colours[val]) }
        if label:
            res[ids[index]]["label"] =  "%s (%.2f)" % (ids[index], val)
    return res


def strength_color(vector, label=True, ids=None, bcf=default_bcf):
    """Given a vector (a c_i), it normalises it (such that no element is larger
    than 1) and assigns a colour to each node.

    If label is True, then the node labels are changed to "NODE_ID (col = VALUE)",
    where the VALUE is the normalised value in the c_i vector given.

    To control IDs of nodes, the ids parameter is a dict-like object that maps
    vector indices to node IDs from the graph. By default, _tostr_dict is used,
    which only converts the IDs to strings (e.g. 3 -> "3").

    bcf is a function of type lambda val: css_colour_as_string. val is a float
    in the interval [0,1]. The default function is
    lambda v: "rgb(%d,0,0)" % int(round(v * 255)).
    """
    if ids is None:
        ids = _tostr_dict()

    vector = vector / vector.sum()
    values = np.unique(vector.flat)
    values = values[1:] if len(values) > 1 and values[0] == 0.0 else values
    colours = {0.0: 0.0}
    for index, val in enumerate(values):
        colours[val] = (index+1)/len(values)

    res = {}
    for index, val in enumerate(vector.flat):
        res[ids[index]] = {"color": bcf(colours[val]) }
        if label:
            res[ids[index]]["label"] =  "%s (%.2f)" % (ids[index], val)
    return res

def shortcut(edges, vector, json_path):
    dobj = edgelist(edges)
    dobj.add_properties(strength_color(vector.copy()))
    dobj.add_properties(strength_size(vector.copy()))
    dobj.json(json_path)
