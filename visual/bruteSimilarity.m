function [ c ] = bruteSimilarity( adj, miu, iterations )
%SIMILARITY Dummiliy compute similarity using iterations
%   The graph needs to be connected.
%   adj = adjanceny matrix
%   iterations = no. of iterations to perform
nodes = size(adj,1);

Dnum = 1 ./ repmat(sum(adj')',1, nodes);
D = bsxfun(@times, adj, Dnum);

c = speye(nodes);
for j=1:iterations
    c = c + miu * D;
    miu = miu^2;
    D = D^2;
end



end

