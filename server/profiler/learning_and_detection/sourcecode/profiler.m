function Model = profiler(name, algorithm, columns, output_dir)
    opts = detectImportOptions(name);
    tabcontent = readtable(name, opts);
    
    training_cols = split(columns, ",");
    rawprdata = tabcontent(:,training_cols);
    rawprdata = rmmissing(rawprdata);
   
    if algorithm == "svm"
        Model = fitcsvm(rawprdata, ones(height(rawprdata), 1), Standardize=true, KernelScale="auto", OutlierFraction=0);
        path = strsplit(name, "/");
        savepath = strcat(output_dir, "SVMtrainedModel_");
    else
        Model = iforest(rawprdata);
        path = strsplit(name, "/");
        savepath = strcat(output_dir, "iforesttrainedModel_");
    end

    savepath = strcat(savepath, path(length(path)));
    [p,f]=fileparts(savepath);
    savepath = fullfile(p,f);
    
    saveLearnerForCoder(Model, savepath)
    %./run_profiler.sh "/usr/local/MATLAB/R2023b/" "../dat_files/(code)_2557.csv"
end