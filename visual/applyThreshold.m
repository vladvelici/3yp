function [ sparseC ] = applyThreshold( c, k )
%APPLYTHRESHOLD All numbers that are below the kth maximum get set to 0.
    cm = maxk(c,k);
    cm = cm(size(cm,1));
    sparseC = sparse(c.*(c>=cm));
end

