function [ q, z ] = similarity( adj, mu, m )
%SIMILARITY Compute similarity for the undirected graph given.
%   Returns the Q and Z matrixes used to compute similarities between
% nodes.
%
%   Arguments:
%   adj     - adjacency matrix
%   miu     - the penalising factor
%   m       - the number of eigenvalues/vectors to use

neigh = sum(adj,2);
neighinv = neigh.^-1;
w = diag(neighinv);
wHalf = diag(sqrt(neighinv));

A = wHalf * adj * wHalf;
[vec, val] = eigs(A,m);

z = diag(sqrt(neigh)) * vec * (1-mu*val).^-1;
q = vec' * w * vec;

end

