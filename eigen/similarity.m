function [ q, z, l ] = similarity( adj, mu, m )
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

N = size(adj,1);
l = zeros(N,1);
veci = vec';
for nodeId=1:N
    ci = zeros(N,1);
    for i = 1:m
        ci = ci + wHalf * vec(:,i) * (1/(1-(mu*val(i,i)))) * veci(i, nodeId) * neigh(i);
    end
    l(nodeId) = norm(ci);
end

end

