function [ adj ] = fromFacebookData( path )
    raw = csvread(path);
    
    % friends is a symmetric relationship
    % raw = [raw(:,1), raw(:,2); raw(:,2), raw(:,1)];
    
    adj = sparse(raw(:,1), raw(:,2), ones(size(raw,1),1));
end