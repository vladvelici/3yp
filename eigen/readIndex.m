function [ q, z ] = readIndex( index )
    vars = {'q', 'z'};
    res = load(index, vars{:});
    q = res.q;
    z = res.z;
end

