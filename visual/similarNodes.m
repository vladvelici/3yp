function [ sim ] = similarNodes( c, node )
%SIMILARNODES Get the list of nodes sorted by similarity
% c is the c matrix obtained from similarity() function
% node is the node id to compute similarities for
% This function computes the distances (using dist()) to all
% the nodes and returns a sorted list sim.
%
% sim has the size (number of nodes, 2). The first column is the distance
% to the node and the second column is the node number.

N = size(c,2);
sim = [zeros(N,1) (1:N)'];
for i = 1:N
    sim(i,:) = [dist(c, node, i) i];
end
sim = sortrows(sim, 1);
end

