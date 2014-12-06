function [ d ] = dist( c, a, b )
%DIST magnitude of difference
    d = norm(c(:,a) - c(:,b));
end