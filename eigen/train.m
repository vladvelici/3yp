function [] = train( csv_path, mu, k, index_path )
    raw = csvread(csv_path);
    adj = sparse(raw(:,1), raw(:,2), ones(size(raw,1),1));
    [q, z] = similarity(adj, mu, int64(k));
    save(index_path, 'q', 'z');
end

