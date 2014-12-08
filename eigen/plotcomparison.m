function [m,diffs] = plotcomparison( tops_brute, adj, mu )

m = 10:5:199;
diffs = length(m);
for i=1:diffs
    [qtmp, ztmp] = similarity(adj,mu,m(i));
    te = mkdif(qtmp,ztmp);
    diffs(i) = calcdiff(tops_brute, te);
end
plot(m,diffs);
end

