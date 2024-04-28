function detection_matrix = SVM_detect_anomalies(Model_name, algorithm, columns, period)
    Model_name = strrep(Model_name, "'", "");
    Model = loadLearnerForCoder(Model_name);
    
    detection_cols = split(columns, ",");
    period = str2double(period);

    client = tcpclient("localhost",6112, "Timeout", period);
    
    pause on
    
    while true
        data = read(client,client.NumBytesAvailable,"string");
        
        if ~isempty(data)
            data = str2double(split(splitlines(data), ","));
            datetime = data(:,1);
            data = data(:,2:width(data));
            rawprdata = array2table(data, 'VariableNames', detection_cols);
            rawprdata = rmmissing(rawprdata);
            
            if algorithm == "svm"
                [~, anomaly_score] = predict(Model, rawprdata);
                anomaly_status = anomaly_score < 0;
            else
                [anomaly_status, anomaly_score] = isanomaly(Model, rawprdata);
            end
            
            detection_matrix = num2str([datetime' anomaly_score' anomaly_status']);
            write(client, num2str(strlength(detection_matrix)), "string")
            write(client, detection_matrix, "string")
       

        end
        pause(period);
    end
    %./run_profiler.sh "/usr/local/MATLAB/R2023b/" "../dat_files/(code)_2557.csv"
end