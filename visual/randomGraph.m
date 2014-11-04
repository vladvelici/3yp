function [ adj ] = randomGraph( nodes, edges, directed )
%RANDOMGRAPH Generates a random connected graph
%   returns adjacency matrix

adj = speye(nodes);
% make it connected
seq = randperm(nodes);
for i=2:nodes
    adj(seq(i-1),seq(i)) = 1;
end

% add the rest of the edges
edges = edges - nodes + 1;
while edges > 0
    edge = randi([1 nodes], 2,1);
    if adj(edge(1),edge(2)) == 0
        adj(edge(1),edge(2)) = 1;
        if not(directed)
            adj(edge(2), edge(1)) = 1;
        end
        edges = edges - 1;
    end
end

end

