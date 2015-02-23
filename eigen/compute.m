function [ res ] = compute( index, compute_edges, out_graph )
    [q,z] = readIndex(index);
    edges = csvread(compute_edges);

    index = zeros(size(z,1), size(z,1)) - 1;
    
    res = zeros(size(edges,1), 4);
    for i = 1:size(edges,1)
        if index(edges(i,1), edges(i,2)) == -1 
            index(edges(i,1), :) = simList(q,z,edges(i,1));
        end
        % score = sim2(q,z,edges(i,1),edges(i,2));
        score = index(edges(i,1), edges(i,2));
        res(i,:) = [edges(i,1) edges(i,2) score min(index(edges(i,1), :))];
    end

    if strcmp(out_graph,'') == 0
        csvwrite(out_graph, res);
    end
end

