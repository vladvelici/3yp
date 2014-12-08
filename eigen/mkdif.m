function [ tops ] = mkdif( q,z )
N = size(z,1);
tops = zeros(N,N);
for i=1:N
    tp = top(q,z,i);
    tp = round(tp(:,2));
    for j=1:N
        tops(tp(j),i) = j;
    end
end

end