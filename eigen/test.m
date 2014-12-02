adj = [1 0 1 0;
       0 1 1 1;
       1 1 1 0
       0 1 0 1];
adj = sparse(adj);
disp('Symmetric adjancency: (1-yes, 0-no)');
disp(issymmetric(adj));

mu = 1/2;
m = 4;

neigh = sum(adj,2);
whalf = diag(sqrt(neigh.^-1));

A = whalf * adj * whalf;
[vec, val] = eigs(A);
val=sparse(val);

[Qcp, Zcp, Lcp, Ccp] = similarity(adj, mu, m);

z = zeros(m,m);
for i=1:m
    for j=1:m
        z(i,j) = (vec(i,j)*sqrt(neigh(i)))/(1-mu*val(j,j));
    end
end

disp('z == Zcp:')
disp(z-Zcp < 1e-5);

display(z); display(Zcp);

display('Now computing Q...');
q = zeros(m,m);
w = diag(neigh.^-1);
for i=1:m
    for j=1:m
        q(i,j) = vec(:,i)'*w*vec(:,j);
    end
end

disp('q == Qcp:')
disp(q-Qcp < 1e-5);
display(q); display(Qcp);

