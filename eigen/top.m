function [ tp ] = top( q,z,l,nodeId )
%TOP Returns the top related nodes

s = simList(q,z,nodeId);

[s, nd] = sort(s);
tp = [s nd];
end

