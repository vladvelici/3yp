function [ ] = trainText( csv_path, mu, k, output_path )
%TRAINTEXT Makes the eigen computation and saves the resulting
% matrices in plain text in the following format:
% - first line contains two integer values: the size of Q
% - the values of Q, space separated
% - two integer values, the size of Z
% - the value of Z

    disp('input parameters:');

    disp(csv_path);
    disp(mu);
    disp(k);
    disp(output_path);

       disp('as a line:');
    mu = str2double(mu);
    k = str2double(k);
    fprintf(1, 'input path: %s\n mu: %f\n k: %d\n output: %s\n', csv_path, mu, k, output_path);

    raw = csvread(csv_path);
    adj = sparse(raw(:,1), raw(:,2), ones(size(raw,1),1));
    [q, z] = similarity(adj, mu, int64(k));

    of = fopen(output_path, 'w');
    fprintf(of, '%d %d\n', size(q,1), size(q,2));
    fprintf(of, '%f ', q);
    fprintf(of, '\n%d %d\n', size(z,1), size(z,2));
    fprintf(of, '%f ', z);
    fclose(of);
end

