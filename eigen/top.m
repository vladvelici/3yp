function [ tp ] = top( q,z,nodeId )
%TOP Returns the top related nodes
s = simList(q,z,nodeId);
[s, nd] = sort(s);
tp = [s nd];
end

