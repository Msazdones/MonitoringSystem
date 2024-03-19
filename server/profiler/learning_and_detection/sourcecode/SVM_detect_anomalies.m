function detection_matrix = SVM_detect_anomalies(Model_name, numberofclients, period)
    Model_name = strrep(Model_name, "'", "");
    Model = loadLearnerForCoder(Model_name);
    
    period = str2double(period);

    client = tcpclient("localhost",6112, "Timeout", period);
    
    numberofclients = str2double(numberofclients);
    
    pause on
    
    while true
        for ci = 1 : numberofclients
            data = read(client,client.NumBytesAvailable,"string");

            if ~isempty(data)
                data = str2double(split(splitlines(data), ","));
                rawprdata = table(data(:,1), data(:,2), data(:,3), data(:,4), data(:,5), data(:,6), 'VariableNames', Model.PredictorNames);
                rawprdata = rmmissing(rawprdata);
        
                [anomaly_status, anomaly_score] = isanomaly(Model, rawprdata);
                detection_matrix = num2str([rawprdata.DATETIME' anomaly_score' anomaly_status']);
                
                write(client, num2str(strlength(detection_matrix)), "string")
                write(client, detection_matrix, "string")
            end
        end
        pause(period);
    end
    %./run_profiler.sh "/usr/local/MATLAB/R2023b/" "../dat_files/(code)_2557.csv"
end