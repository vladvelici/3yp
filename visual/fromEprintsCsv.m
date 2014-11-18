function [ adj ] = fromEprintsCsv( path )
    data = csvread(path);
    data = data(:,1:2)+1;
    unq = unique(data(:));
    display(size(unq));
    adj = sparse(data(:,1),data(:,2),ones(size(data,1),1),size(unq,1),size(unq,1));
end

