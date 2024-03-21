
function SVMModel = SVM_profiler(name, output_dir)
    opts = detectImportOptions(name);
    
    rawprdata = readtable(name, opts);
    
    rawprdata.DATETIME = [];
    rawprdata.TOTALTIME = [];
    rawprdata.RDISK = [];
    rawprdata.WDISK = [];
    rawprdata.RAM = [];

    rawprdata = rmmissing(rawprdata);
    rawprdata = normalize(rawprdata);
    
    SVMModel = ocsvm(rawprdata, ContaminationFraction=0.1, StandardizeData=true, KernelScale="auto");

    path = strsplit(name, "/");
    savepath = strcat(output_dir, "SVMtrainedModel_");
    savepath = strcat(savepath, path(length(path)));
    [p,f]=fileparts(savepath);
    savepath = fullfile(p,f);
    
    saveLearnerForCoder(SVMModel, savepath)
    %./run_profiler.sh "/usr/local/MATLAB/R2023b/" "../dat_files/(code)_2557.csv"
end