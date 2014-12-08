function [ tops ] = bruteMkdif( c )
N = size(c,1);
tops = zeros(N,N);
for i=1:N
    tp = similarNodes(c,i);
    tp = round(tp(:,2));
    for j=1:N
        tops(tp(j),i) = j;
    end
end

end