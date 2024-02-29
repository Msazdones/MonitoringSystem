
function SVMModel = SVM_profiler(name, output_dir)
    opts = detectImportOptions(name);
    opts = setvaropts(opts,"DATETIME",'inputFormat','uuuu-MM-dd HH:mm:ss');
    
    rawprdata = readtable(name, opts);
    rawprdata = rmmissing(rawprdata);
    
    timestamps = arrayfun(@(x) datenum(x) * 86400, rawprdata.DATETIME);
    rawprdata.DATETIME = timestamps;
    SVMModel = ocsvm(rawprdata, ContaminationFraction=0);

    path = strsplit(name, "/");
    savepath = strcat(output_dir, "SVMtrainedModel_");
    savepath = strcat(savepath, path(length(path)));
    [p,f]=fileparts(savepath);
    savepath = fullfile(p,f);
    
    saveLearnerForCoder(SVMModel, savepath)
    %./run_profiler.sh "/usr/local/MATLAB/R2023b/" "../dat_files/(code)_2557.csv"
end