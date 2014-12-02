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

disp('Got eigen...');

gamma = zeros(m,m);
for i=1:m
    gamma(i,i) = (1-mu*val(i,i))^-1;
end

z = diag(sqrt(neigh)) * vec * gamma;

disp('Got Z');
q = vec' * w * vec;
disp('Got Q');

N = size(adj,1);
l = zeros(N,1);
veci = vec';
%c = zeros(size(adj));
for nodeId=1:N
    ci = zeros(N,1);
    for i = 1:m
        ci = ci + z(nodeId,i) * vec(:,i);
    end
    ci = wHalf*ci;
    l(nodeId) = norm(ci);
    if mod(nodeId,100) == 0
        disp(nodeId)
    end
 %   c(:,nodeId)=ci;
end

end

