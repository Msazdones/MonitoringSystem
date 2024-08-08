import config as cfg

def parse_file_to_detection(config, conn):
    host = config["clients"]
    rawdata = reversed(list(conn[host].find({},{"_id": 0}).sort({"_id": -1}).limit(config["samples"])))

    data = {}
    for d in rawdata:
        data.update(d)

    dates = list(data.keys())

    if(len(dates) == 0):
        return {}

    pid_lists = {}
    prdata = []
    for k in dates:
        date = cfg.datetime.strptime(str(k), "%Y-%m-%d %H:%M:%S")
        timestamp = int(date.timestamp())

        try:
            if config["pr_target"] == "global":   
                [prdata.append([timestamp, p["name"], p["pid"], float(p["CPU"]), float(p["RAM"]), float(p["RDISK"]), float(p["WDISK"])]) for p in data[k]]
            else:  
                [prdata.append([timestamp, p["name"], p["pid"], float(p["CPU"]), float(p["RAM"]), float(p["RDISK"]), float(p["WDISK"])]) for p in data[k] if p["name"] == config["pr_target"]]

        except Exception as error:
            print("No data structure found", error)      
    
    df = cfg.pd.DataFrame(prdata, columns=["Timestamp", "Prname", "PID", "CPU", "RAM", "RDISK", "WDISK"])
   
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
        df = parse_file_to_detection(config, conn)

        predictions = []
        if df.shape[0] != 0:
            if config["pr_target"] == "global":
                df = cfg.aux.process_R_and_W(df)
                df = cfg.aux.get_encoded_instants(df)
                df = df[features]

                predictions.append(("global", model.predict(df), model.score_samples(df)))
                
            else:
                df = df.groupby("PID")
                
                for p, g in df:
                    g = cfg.aux.process_R_and_W(g)
                    g = cfg.aux.get_encoded_instants(g)
                    g = g[features]

                    predictions.append(("global", p, model.predict(df), model.score_samples(df)))

        else:
            print("De momento no hay muestras.")
            cfg.time.sleep(config["period"])

def advanced_mode_detection(model, features, config, conn):
    while True:
        #[x for x in range(0, 1440, 30)]
        date = list(list(conn[config["clients"]].find({},{"_id": 0}).sort({"_id": -1}).limit(1))[0].keys())[0]
        #list(conn[config["clients"]].find({},{"_id": 0}).sort({"_id": -1}).limit(1))
        pass

#{"alg", "model", "clients", "samples", "period", "pr_target"} 4683