function [ ci ] = similarity( adj, nodeId, miu, m )
%SIMILARITY Compute the vector Ci for node nodeId (CnodeId)
%   adj     - adjacency matrix
%   nodeId  - node id to compute the similarity vector for
%   miu     - the penalising factor
%   m       - the number of eigenvalues/vectors to use

neigh = sqrt(sum(adj,2));
whalf = diag(neigh.^-1);
A = whalf * adj * whalf;

if m <= 0
    [vec, val] = eigs(A,size(A,1));
    m = size(vec,2);
else
    [vec, val] = eigs(A,m);
end

veci = vec'; % assume real symmetric matrix

ci = zeros(size(A,1),1);
for i = 1:m
    ci = ci + whalf * vec(:,i) * (1/(1-(miu*val(i,i)))) * veci(i, nodeId) * neigh(i);
end

end

