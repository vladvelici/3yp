function [ adj ] = fromEprintsCsv( path )
    data = csvread(path);
    data = data(:,1:2)+1;
    % force symmetric graph;
    unq = unique(data(:));
    data = [data(:,1) data(:,2); data(:,2) data(:,1)];
    display(size(unq));
    adj = sparse(data(:,1),data(:,2),ones(size(data,1),1),size(unq,1),size(unq,1));
end

