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

// List of nodes
func (g *Graph) NodeList() []*Node {
	res := make([]*Node, 0, len(g.Nodes))
	for _, node := range g.Nodes {
		res = append(res, node)
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

// Remove random edges, keeping track of them.
// There might not be n edges that can be removed.
func (g *Graph) RemoveRandomEdges(n int) []*Edge {
	var result []*Edge

	cutout := 0
	nodeList := g.NodeList()

	for i := 0; i < n; {
		if cutout >= 10 {
			return result
		}
		rmv := rand.Intn(len(nodeList))
		node := nodeList[rmv]

		if len(node.Neibourghs) == 1 {
		}

		cutout = 0
	}
}
