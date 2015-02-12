package main

// Type to represent an edge set.
type Edge struct {
	From, To int
}

// Represents a node in a graph.
type Node struct {
	Id         int
	Neibourghs map[int]*Node
}

// Create a new node.
func NewNode(id, set int) *Node {
	return &Node{
		id,
		make(map[int]*Node),
	}
}

// Represents an undirected graph that forms connected graphs.
type Graph struct {
	Nodes map[int]*Node
}

// Create a new graph.
func NewGraph() *Graph {
	return &Graph{
		make(map[int]*Node),
	}
}

// Fetches the node by ID. Creates the node if it does not exist.
func (g *Graph) fetch(node int) *Node {
	f, ok := g.Nodes[node]
	if !ok || f == nil {
		f = NewNode(id, -1)
		g.Nodes[node] = f
	}
	return f
}

// List of edges to be printed out.
func (g *Graph) EdgeList() []*Edge {
	res := make([]*Edge, 0)
	for nid, node := range g.Nodes {
		for toId, _ := range node.Neibourghs {
			res = append(res, &Edge{nid, toId})
		}
	}
	return res
}

// Add a directed edge, taking care of connected components.
// Panics if either from or to are nil.
func (g *Graph) directedEdge(from, to *Node) {
	if _, ok := from.Neibourghs[to.Id]; ok {
		return
	}
	from.Neibourghs[to.Id] = append(from.Neibourghs[to.Id], to)
}

func (g *Graph) AddEdge(fromId, toId int) {
	from := g.fetch(fromId)
	to := g.fetch(toId)
	g.directedEdge(from, to)
	g.directedEdge(to, from)
}

func (g *Graph) addNode(node *Node) {
	g.Nodes[node.Id] = node
}

// Internal type used for traversals
type tr_index map[int]interface{}

// Set node as visited.
func (t tr_index) visit(node *Node) {
	t[node.Id] = nil
}

// Check if a node was visited.
func (t tr_index) visited(node *Node) bool {
	_, ok := t[node.Id]
	return ok
}

// Return a list of connected graphs.
func (g *Graph) ConnectedGraphs() []*Graph {
	result := make([]*Graph, 0)

	index := make(tr_index)

	for id, node := range g.Nodes {
		if index.visited(node) {
			continue
		}
		graph := NewGraph()
		Bfs(node, index.visit, index.visited, graph.addNode)
		result = append(result, graph)
	}

	return result
}

type Mst struct {
	Edges map[int]map[int]interface{}
}

func (m Mst) Add(from, to int) {
	f := m.Edges[from]
	if f == nil {
		m.Edges[from] = make(map[int]interface{})
	}
	m.Edges[from][to] = nil
}

// Minimum spanning tree computation.
func (g *Graph) Mst() []*Edge {
	var root *Node
	for _, node := range g.Nodes {
		root = node
		break
	}

	if root == nil {
		return nil
	}

	index := make(tr_index)
	res := make([]*Edge, 0)

}

// Remove random edges, keeping track of them.
//
// It does not remove critical edges. Computes the minimum spanning tree and only removes
// random edges that are not part of it.
//
// If it fails 10 times in a row, it randomly cancels
func (g *Graph) RemoveRandomEdges(n int) []*Edge {
	var result []*Edge
	edges := g.EdgeList()
	noEdges := len(edges)
	cutout := 0
	for i := 0; i < n; {
		if cutout >= 10 {
			return result
		}
		edgIndex := rand.Intn(noEdges)
		edge := edges[edgIndex]

		if !IsPathRestricted(g.Nodes[edge.From], g.Nodes[edge.To], edge) {
			cutout++
			continue
		}
		cutout = 0
		// remove edge
		g.Nodes[4]
	}

}

// Removes the inverse edge of edg.
func rmvUndirFromList(lst []*Edge, edg *Edge) []*Edge {
	from := edg.To
	to := edg.From
	for i, e := range lst {
		if e.From == from && e.To == to {
			return rmvElementFromList(lst, i)
		}
	}
}

// Removes the edge at position el, by moving the end in that position...
func rmvElementFromList(lst []*Edge, el int) []*Edge {
	last := len(lst) - 1
	lst[el], lst[last] = lst[last], nil
	return lst[:len(lst)]
}
