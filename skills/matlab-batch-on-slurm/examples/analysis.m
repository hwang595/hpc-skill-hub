function analysis()
outputDir = getenv('OUTPUT_DIR');
if isempty(outputDir)
    outputDir = 'results';
end

if ~exist(outputDir, 'dir')
    mkdir(outputDir);
end

fprintf('MATLAB version: %s\n', version);
fprintf('MATLAB release: %s\n', version('-release'));
fprintf('Timestamp: %s\n', datestr(now, 31));
fprintf('MATLAB_ENTRYPOINT: %s\n', getenv('MATLAB_ENTRYPOINT'));
fprintf('MATLAB_WORKDIR: %s\n', getenv('MATLAB_WORKDIR'));
fprintf('OUTPUT_DIR: %s\n', outputDir);
fprintf('SLURM_CPUS_PER_TASK: %s\n', getenv('SLURM_CPUS_PER_TASK'));
fprintf('maxNumCompThreads: %d\n', maxNumCompThreads);

try
    fprintf('Licenses in use:\n');
    disp(license('inuse'));
catch err
    fprintf('Unable to query licenses in use: %s\n', err.message);
end

rng(1);
x = (1:10)';
y = cumsum(randn(10, 1));

csvPath = fullfile(outputDir, 'matlab-demo.csv');
summaryPath = fullfile(outputDir, 'matlab-summary.txt');

data = table(x, y, 'VariableNames', {'x', 'y'});
writetable(data, csvPath);

fid = fopen(summaryPath, 'w');
cleanup = onCleanup(@() fclose(fid));
fprintf(fid, 'MATLAB demo complete\n');
fprintf(fid, 'rows: %d\n', numel(y));
fprintf(fid, 'mean_y: %.6f\n', mean(y));
fprintf(fid, 'maxNumCompThreads: %d\n', maxNumCompThreads);
clear cleanup;

fprintf('Wrote: %s\n', csvPath);
fprintf('Wrote: %s\n', summaryPath);
end
