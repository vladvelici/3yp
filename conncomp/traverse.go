package main

import "container/list"

// Breath first search graph traversal.
// visit - sets a node as visited.
// visited - checks if a node was visited.
// f - function that is called at each visit, for convenience.
func Bfs(root *Node, visit func(*Node), visited func(*Node) bool, f func(*Node)) {
	todo := list.New()
	todo.PushBack(root)

	for todo.Len() > 0 {
		el := todo.Front()
		node := el.Value.(*Node)
		todo.Remove(el)

		if visited(node) {
			continue
		}

		visit(node)
		f(node)

		for _, ngh := range node.Neibourghs {
			todo.PushBack(ngh)
		}
	}
}
