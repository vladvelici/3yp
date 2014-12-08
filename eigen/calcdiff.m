function [ d ] = calcdiff( tops1, tops2 )
    N = size(tops1,1);
    normalising = 1/(N*N*N);
    sum = 0;
    for i=1:N
        for j=1:N
            disp = abs(tops1(i,j) - tops2(i,j));
            sum = sum + disp;
        end
    end
    d = normalising * sum;
end

