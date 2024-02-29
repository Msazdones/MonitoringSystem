
function detection_matrix = detect_anomalies(Model_name, observations_file, output_dir, alg)
    Model = loadLearnerForCoder(Model_name);

    rawprdata = readtable(observations_file, 'Format','%s %f %f %f %f %f');
    rawprdata.Properties.VariableNames = ["DATETIME","CPU","RAM","RDISK","WDISK","TOTALTIME"];
    rawprdata = rmmissing(rawprdata);

    timestamp = rawprdata.DATETIME;
    rawprdata = removevars(rawprdata, {'DATETIME'});
    
    [anomaly_status, anomaly_score] = isanomaly(Model, rawprdata);

    detection_matrix = table(timestamp, anomaly_score, anomaly_status);
    
    path = strsplit(observations_file, "/");
    
    savepath = strcat(output_dir, "det_");
    if alg == "svm"
        writetable(detection_matrix, strcat(savepath, path(length(path))));
    elseif alg == "iforest"
        writetable(detection_matrix, strcat(savepath, path(length(path))));
    end
    %./run_profiler.sh "/usr/local/MATLAB/R2023b/" "../dat_files/(code)_2557.csv"
end