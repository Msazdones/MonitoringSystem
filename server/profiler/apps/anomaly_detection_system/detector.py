import config as cfg

def parse_file_for_normal_detection(config, conn):
    host = config["clients"]

    dates = reversed(list(conn[host].aggregate([{"$sort": {"_id": 1}}, {"$group": {"_id": "$date"}}, {"$sort": {"_id": -1}}, {"$limit": config["samples"]}])))
   
    data = []
    for d in dates:
        date = cfg.datetime.strptime(str(d["_id"]), "%Y-%m-%d %H:%M:%S")
        timestamp = int(date.timestamp())

        rawdata = conn[host].find({"date" : d["_id"]}, {"_id": 0}) 
        
        if config["pr_target"] == "global": 
            [data.append([timestamp, jd["label"], jd["name"], jd["data"]["pid"], float(jd["data"]["CPU"]), float(jd["data"]["RAM"]), float(jd["data"]["RDISK"]), float(jd["data"]["WDISK"])]) for jd in rawdata]
        else:
            [data.append([timestamp, jd["label"], jd["name"], jd["data"]["pid"], float(jd["data"]["CPU"]), float(jd["data"]["RAM"]), float(jd["data"]["RDISK"]), float(jd["data"]["WDISK"])]) for jd in rawdata if jd["name"] == config["pr_target"]]
        
    df = cfg.pd.DataFrame(data, columns=["Timestamp", "Label", "Prname", "PID", "CPU", "RAM", "RDISK", "WDISK"])
   
    return df

def parse_file_for_advanced_detection(conn, config, intervals, interval):
    host = config["clients"] 
    date = list(conn[host].aggregate([{"$sort": {"_id": 1}}, {"$group": {"_id": "$date"}}, {"$sort": {"_id": -1}}, {"$limit": 1}]))[0]["_id"]
        
    instant = date[11:16].split(":")
    instant = (int(instant[0])* 60) + int(instant[1])  
    hl = intervals[cfg.np.argmax(intervals > instant)]
    ll = intervals[cfg.np.where(intervals == hl)[0][0] - 1]

    dates = []
    for i in range(0, interval):         
        dates.append(date[0:11] + str(((ll + i) // 60) % 24) + ":" + str((ll + i) % 60) + ":*.")

    tts = hl - instant  
    print("Waiting for samples...")
    cfg.time.sleep(tts * 60)

    data = []
    for d in dates:
        if config["pr_target"] == "global":
            rawdata = conn[host].find({"date": {"$regex": d}}, {"_id" : 0})
        else:
            rawdata = conn[host].find({"name" : config["pr_target"], "date": {"$regex": d}}, {"_id" : 0})

        for r in rawdata:
            date = cfg.datetime.strptime(str(r["date"]), "%Y-%m-%d %H:%M:%S")
            timestamp = int(date.timestamp())
            data.append([timestamp, r["name"], r["data"]["pid"], float(r["data"]["CPU"]), float(r["data"]["RAM"]), float(r["data"]["RDISK"]), float(r["data"]["WDISK"])])

    df = cfg.pd.DataFrame(data, columns=["Timestamp", "Prname", "PID", "CPU", "RAM", "RDISK", "WDISK"])
    
    return df, ll + hl

def log_detection_results(predictions, alg, logfile):
    lf = open(logfile, "a")
    headers = cfg.logheaders.copy()
    for c in predictions[0][3].columns.values:
        headers.append(c)

    log_line = []
    for p in predictions:
        for i in range(0, len(p[0])):
            l = [str(p[0][i]), str(p[1][i]), str(p[2]), str(p[4]), str(p[5]), ("Negativo" if p[0][i]==1 else "Positivo")]
            l.append(str(p[3].index[i]))
            for c in p[3].columns.values:
                l.append(str(p[3].iloc[i][c]))
            log_line.append(l)
            line = ",".join(l) + "\n"
            lf.write(line)

    print(cfg.pd.DataFrame(log_line, columns=headers))
    print("----------------------------------------------------------------")
    lf.close()

def create_log_file(pr_name):
    filename = cfg.log_route + pr_name + "_" + cfg.datetime.today().strftime('%Y-%m-%d_%H:%M:%S') + ".csv"
    f = open(filename, "a")
    f.write(cfg.LOG_HEADERS)
    f.close()
    
    return filename

def detection(config, conn):
    logfile = create_log_file(config["pr_target"])

    mlpkt = cfg.joblib.load(config["model"])
    model = mlpkt[0]
    scaler = mlpkt[1]
    interval = mlpkt[2]
    features = mlpkt[3]

    if(set(features) & set(cfg.normal_csv_headers.split(","))):
        normal_mode_detection(model, scaler, features, config, conn, logfile)
    
    elif(set(features) & set(cfg.advanced_csv_headers.split(","))):
        advanced_mode_detection(model, scaler, interval, features, config, conn, logfile)
    
    else:
        print("No common features were found.")
        return -1

def normal_mode_detection(model, scaler, features, config, conn, logfile):
    while True:
        df = parse_file_for_normal_detection(config, conn)

        predictions = []
        if df.shape[0] != 0:
            if config["pr_target"] == "global":
                df = cfg.aux.process_R_and_W(df)
                df = cfg.aux.get_encoded_instants(df)
                df = df[features]

                if config["alg"] == "ocsvm":
                    prediction = sklearn_anom_detection(model, scaler, df, config,  "global")

                elif config["alg"] == "svm":
                    prediction = sklearn_class_detection(model, scaler, df, config,  "global")
                
                elif config["alg"] == "nn_anom":
                    prediction = keras_nn_anom_detection(model, scaler, df, config, "global")

                elif config["alg"] == "nn_class":
                    prediction = keras_nn_class_detection(model, scaler, df, config, "global")
                
                predictions.append(prediction)
                log_detection_results(predictions, config["alg"], logfile)
                
            else:
                df = df.groupby("PID")
                
                for p, g in df:
                    g = cfg.aux.process_R_and_W(g)
                    g = cfg.aux.get_encoded_instants(g)
                    g = g[features]

                    if config["alg"] == "ocsvm":
                        prediction = sklearn_anom_detection(model, scaler, g, config, p)

                    elif config["alg"] == "svm":
                        prediction = sklearn_class_detection(model, scaler, df, config, p)
                    
                    elif config["alg"] == "nn_anom":
                        prediction = keras_nn_anom_detection(model, scaler, df, config, p)
                    
                    elif config["alg"] == "nn_class":
                        prediction = keras_nn_class_detection(model, scaler, df, config, p)

                    predictions.append(prediction)
                    log_detection_results(predictions, config["alg"], logfile)
        else:
            print("De momento no hay muestras.")
        
        cfg.time.sleep(config["period"])


def advanced_mode_detection(model, scaler, interval, features, config, conn, logfile):
      
    intervals = cfg.np.array([x for x in range(0, 1440, interval)])

    while True:
        df, encinterval = parse_file_for_advanced_detection(conn, config, intervals, interval)
        
        predictions = []
        if df.shape[0] != 0:
            if config["pr_target"] == "global":
                df = cfg.aux.process_R_and_W(df)
                df = cfg.aux.get_data_stats(df, interval, 0)
                df["Interval"] = encinterval
                df = df[features]

                if config["alg"] == "ocsvm":
                    prediction = sklearn_anom_detection(model, scaler, df, config,  "global")

                elif config["alg"] == "svm":
                    prediction = sklearn_class_detection(model, scaler, df, config,  "global")
                
                elif config["alg"] == "nn_anom":
                    prediction = keras_nn_anom_detection(model, scaler, df, config, "global")
                
                elif config["alg"] == "nn_class":
                    prediction = keras_nn_class_detection(model, scaler, df, config, "global")
                
                predictions.append(prediction)
                log_detection_results(predictions, config["alg"], logfile)

            else:
                df = df.groupby("PID")
                for p, g in df:
                    g = cfg.aux.process_R_and_W(g)
                    g["Prname"] = config["pr_target"]
                    g["PID"] = p
                    g, b = cfg.aux.get_data_stats(g, interval, 1)
                    g["Interval"] = encinterval
                    g = g[features]

                    if config["alg"] == "ocsvm":
                        prediction = sklearn_anom_detection(model, scaler, g, config, p)
                    
                    elif config["alg"] == "svm":
                        prediction = sklearn_class_detection(model, scaler, df, config, p)
                    
                    elif config["alg"] == "nn_anom":
                        prediction = keras_nn_anom_detection(model, scaler, df, config, p)
                    
                    elif config["alg"] == "nn_class":
                        prediction = keras_nn_class_detection(model, scaler, df, config, p)

                    predictions.append(prediction)
                    log_detection_results(predictions, config["alg"], logfile)
        
        else:
            print("De momento no hay muestras.")

def sklearn_anom_detection(model, scaler, df, config, p):
    dfp = cfg.pd.DataFrame(scaler.transform(df), columns=df.columns.values)
    
    scores = model.score_samples(dfp)
    prediction = (((scores >= config["threshold"]).astype(int)), scores, config["threshold"], df, config["pr_target"], p)
    
    return prediction

def sklearn_class_detection(model, scaler, df, config, p):
    dfp = cfg.pd.DataFrame(scaler.transform(df), columns=df.columns.values)

    prediction = (model.predict(dfp), model.decision_function(dfp), config["threshold"], df, config["pr_target"], p)

    return prediction

def keras_nn_anom_detection(model, scaler, df, config, p):
    dfp = cfg.pd.DataFrame(scaler.transform(df), columns=df.columns.values) 
    
    preds = model.predict(dfp)
    ecm = cfg.np.mean(cfg.np.power(dfp - preds, 2), axis=1)

    status = cfg.np.array([0 if e > config["threshold"] else 1 for e in ecm])

    prediction = (status, ecm, config["threshold"], df, config["pr_target"], p)
    
    return prediction

def keras_nn_class_detection(model, scaler, df, config, p):
    dfp = cfg.pd.DataFrame(scaler.transform(df), columns=df.columns.values) 
    
    preds = model.predict(dfp)

    prediction = ([cfg.np.argmax(p) for p in preds], [cfg.np.amax(p) for p in preds], config["threshold"], df, config["pr_target"], p)
    
    return prediction