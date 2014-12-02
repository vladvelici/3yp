function [ s ] = simList( q,z,l,nodeId )

nodes = size(z,1);
s = zeros(nodes,1);
for i=1:nodes
    s(i) = sim2(q,z,l,nodeId,i);
end

end

