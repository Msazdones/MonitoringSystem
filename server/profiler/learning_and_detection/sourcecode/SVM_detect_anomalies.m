
function detection_matrix = SVM_detect_anomalies(Model_name, observations_file, output_dir)
    Model_name = strrep(Model_name, "'", "");
    Model = loadLearnerForCoder(Model_name);
   
    opts = detectImportOptions(observations_file);
    
    rawprdata = readtable(observations_file, opts);
    rawprdata = rmmissing(rawprdata);
    
    [anomaly_status, anomaly_score] = isanomaly(Model, rawprdata);

    detection_matrix = table(rawprdata.DATETIME, anomaly_score, anomaly_status);
    
    path = strsplit(observations_file, "/");
    
    savepath = strcat(output_dir, "det_");

    writetable(detection_matrix, strcat(savepath, path(length(path))), 'WriteMode','append');

    %./run_profiler.sh "/usr/local/MATLAB/R2023b/" "../dat_files/(code)_2557.csv"
end