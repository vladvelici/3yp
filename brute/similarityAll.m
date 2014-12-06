function [ c ] = similarityAll( adj, miu, m, k )
%SIMILARITYALL Compute similarity of all nodes
%   adj - adjancency matrix
%   miu - penalising factor
%   m   - number of eigenvectors/eigenvalues to use
%   k   - only keep largest kth numbers (c(i) is set to 0 if c(i)<kth
%   largest number in c)


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

c = sparse(size(A,1),size(A,2));
for nodeId = 1:size(c,1);
    tmpC = zeros(size(A,1),1);
    for i = 1:m
        tmpC = tmpC + whalf * vec(:,i) * (1/(1-(miu*val(i,i)))) * veci(i, nodeId) * neigh(i);
    end
    c(:,nodeId) = applyThreshold(tmpC,k);
    if mod(nodeId,10) == 0
        disp(nodeId);
    end
end

end

