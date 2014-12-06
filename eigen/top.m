function [ tp ] = top( q,z,l,nodeId )
%TOP Returns the top related nodes
s = simList(q,z,l,nodeId);
[s, nd] = sort(s, 'descend');
tp = [s nd];
end

