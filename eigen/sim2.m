function [ similarity ] = sim2( q,z,l,a,b )
%SIM2 Compute similarity between nodes a and b.
similarity = (z(a,:)*q*z(b,:)')/(l(a)*l(b));
end

