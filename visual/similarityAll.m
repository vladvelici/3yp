function [ c ] = similarityAll( adj, miu, m )
%SIMILARITYALL Compute similarity of all nodes
%   adj - adjancency matrix
%   miu - penalising factor
%   m   - number of eigenvectors/eigenvalues to use

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

c = zeros(size(A));
for nodeId = 1:size(c,1);
    for i = 1:m
        c(:,nodeId) = c(:,nodeId) + whalf * vec(:,i) * (1/(1-(miu*val(i,i)))) * veci(i, nodeId) * neigh(i);
    end
end

end

