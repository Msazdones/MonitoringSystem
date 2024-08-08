import config as cfg

def parse_file_to_normal_detection(config, conn):
    host = config["clients"]

    dates = reversed(list(conn[host].aggregate([{"$sort": {"_id": 1}}, {"$group": {"_id": "$date"}}, {"$sort": {"_id": -1}}, {"$limit": config["samples"]}])))
   
    data = []
    for d in dates:
        date = cfg.datetime.strptime(str(d["_id"]), "%Y-%m-%d %H:%M:%S")
        timestamp = int(date.timestamp())

        rawdata = conn[host].find({"date" : d["_id"]}, {"_id": 0}) 
        
        if config["pr_target"] == "global": 
            [data.append([timestamp, jd["name"], jd["data"]["pid"], float(jd["data"]["CPU"]), float(jd["data"]["RAM"]), float(jd["data"]["RDISK"]), float(jd["data"]["WDISK"])]) for jd in rawdata]
        else:
            [data.append([timestamp, jd["name"], jd["data"]["pid"], float(jd["data"]["CPU"]), float(jd["data"]["RAM"]), float(jd["data"]["RDISK"]), float(jd["data"]["WDISK"])]) for jd in rawdata if jd["name"] == config["pr_target"]]
        
    df = cfg.pd.DataFrame(data, columns=["Timestamp", "Prname", "PID", "CPU", "RAM", "RDISK", "WDISK"])
   
    return df

def parse_file_to_advanced_detection(conn, config, intervals, interval):
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
    #cfg.time.sleep(tts * 60)

    data = []
    for d in dates:
        rawdata = conn[host].find({"date": {"$regex": d}}, {"_id" : 0})

        if config["pr_target"] == "global": 
            for r in rawdata:
                date = cfg.datetime.strptime(str(r["date"]), "%Y-%m-%d %H:%M:%S")
                timestamp = int(date.timestamp())

                data.append([timestamp, r["name"], r["data"]["pid"], float(r["data"]["CPU"]), float(r["data"]["RAM"]), float(r["data"]["RDISK"]), float(r["data"]["WDISK"])])
        else:
            for r in rawdata:
                date = cfg.datetime.strptime(str(r["date"]), "%Y-%m-%d %H:%M:%S")
                timestamp = int(date.timestamp())
                
                if r["name"] == config["pr_target"]:
                    data.append([timestamp, r["name"], r["data"]["pid"], float(r["data"]["CPU"]), float(r["data"]["RAM"]), float(r["data"]["RDISK"]), float(r["data"]["WDISK"])])
        
    df = cfg.pd.DataFrame(data, columns=["Timestamp", "Prname", "PID", "CPU", "RAM", "RDISK", "WDISK"])
    
    return df

def log_detection_results(rdata, procinfo, alg, logfile):
        lf = open(logfile, "a")

        pids = list(procinfo.keys())    
        gl  = sum([len(procinfo[i].split("\n"))-1 for i in procinfo.keys()])

        ts = rdata[0:gl]
        rt = rdata[gl:2*gl]
        st = rdata[2*gl:3*gl]

        lsamp = 0
        for i in range(0,len(pids)):
            samp = len(procinfo[pids[i]].split("\n"))-1
            pi = procinfo[pids[i]].split("\n")
            for j in range(0,samp):
                
                if st[j+lsamp] == '1':
                    log_line = "Positivo,"
                else:
                    log_line = "Negativo,"

                log_line = log_line + ts[j+lsamp] + "," + rt[j+lsamp] + "," + st[j+lsamp] + "," + pids[i] + "," + alg + "," + pi[j] + "\n"
                print(log_line)
                lf.write(log_line)
        
        print("----------------------------------------------------------------")
        lf.close()

def create_log_file(pr_name):
    filename = cfg.log_route + pr_name + "_" + cfg.datetime.today().strftime('%Y-%m-%d_%H:%M:%S') + ".csv"
    f = open(filename, "a")
    f.write(cfg.LOG_HEADERS)
    f.close()
    
    return filename

def detection(config, conn):
    #logfile = create_log_file(config["pr_target"])

    model = cfg.joblib.load(config["model"])
    features = model.feature_names_in_

    if(set(features) & set(cfg.normal_csv_headers.split(","))):
        normal_mode_detection(model, features, config, conn)
    
    elif(set(features) & set(cfg.advanced_csv_headers.split(","))):
        advanced_mode_detection(model, features, config, conn)
    
    else:
        print("No common features were  found.")
        return -1

def normal_mode_detection(model, features, config, conn):
    while True:
        df = parse_file_to_advanced_detection(config, conn)

        predictions = []
        if df.shape[0] != 0:
            if config["pr_target"] == "global":
                df = cfg.aux.process_R_and_W(df)
                df = cfg.aux.get_encoded_instants(df)
                df = df[features]

                predictions.append((config["pr_target"], model.predict(df), model.score_samples(df)))
                
            else:
                df = df.groupby("PID")
                
                for p, g in df:
                    g = cfg.aux.process_R_and_W(g)
                    g = cfg.aux.get_encoded_instants(g)
                    g = g[features]

                    predictions.append((config["pr_target"], p, model.predict(df), model.score_samples(df)))

        else:
            print("De momento no hay muestras.")
            cfg.time.sleep(config["period"])

def advanced_mode_detection(model, features, config, conn):
      
    intervals = cfg.np.array([x for x in range(0, 1440, model.interval)])

    while True:
        df = parse_file_to_normal_detection(conn, config, intervals,  model.interval)

#{"alg", "model", "clients", "samples", "period", "pr_target"} 4683