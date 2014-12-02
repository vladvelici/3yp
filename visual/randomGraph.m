function [ adj ] = randomGraph( nodes, edges, directed )
%RANDOMGRAPH Generates a random connected graph
%   returns adjacency matrix

connections = zeros(edges,2);
% make it connected
seq = randperm(nodes);
edge = 1;

for i=2:nodes
    connections(edge,:) = [seq(i-1) seq(i)];
    edge = edge+1;
end

% add the rest of the edges
while edge <= edges
    connections(edge,:) = randi([1 nodes], 1,2);
    edge = edge+1;
end

if not(directed)
    connections = [connections; connections(:,2) connections(:,1)];
end

adj = sparse(connections(:,1), connections(:,2), ones(size(connections,1),1), nodes, nodes);
adj = (speye(nodes) + adj)>0;
end

