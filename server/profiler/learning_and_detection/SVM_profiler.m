
function savepath = SVM_profiler(name, output_dir)
    rawprdata = readtable(name, 'Format','%s %f %f %f %f %f');
    rawprdata.Properties.VariableNames = ["DATETIME","CPU","RAM","RDISK","WDISK","TOTALTIME"];
    rawprdata = rmmissing(rawprdata);

    %timestamp = rawprdata.DATETIME;
    rawprdata = removevars(rawprdata,{'DATETIME'});
    
    SVMModel = ocsvm(rawprdata, ContaminationFraction=0);

    path = strsplit(name, "/");
    savepath = strcat(output_dir, "SVMtrainedModel_");
    savepath = strcat(savepath, path(length(path)));
    [p,f,e]=fileparts(savepath);
    savepath = fullfile(p,f);
    
    saveLearnerForCoder(SVMModel, savepath)
    %./run_profiler.sh "/usr/local/MATLAB/R2023b/" "../dat_files/(code)_2557.csv"
end