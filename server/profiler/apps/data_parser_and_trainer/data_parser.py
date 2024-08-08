import config as cfg

def parse_file_for_training(config, db_conn):
    for host in config["clients"]:
        jsondata = {}
        dates = []
        
        if(config["samples"] == "all"):
            rawdata = db_conn[host].find({},{"_id": 0})
        else:
            rawdata = reversed(list(db_conn[host].find({},{"_id": 0}).sort({"_id": -1}).limit(config["samples"])))

        stepcnt = config["step"] - 1 #para quedarnos siempre con la primera muestra
        cnt = 0
        for d in rawdata:
            cnt = cnt +1 
            if(stepcnt == config["step"]-1): 
                jsondata.update(d)
                stepcnt = 0
            else:
                stepcnt = stepcnt + 1

        dates = list(jsondata.keys())
        if(len(dates) == 0):
            continue
        
        cnt = 0#
        tot = len(dates)#
        print("Primera etapa")#
        data = []
        # revisar esto para optimizarlo
        for k in dates:
            cnt+=1#
            print(cnt, "/", tot)#

            date = cfg.datetime.strptime(str(k), "%Y-%m-%d %H:%M:%S")
            timestamp = int(date.timestamp())
            
            try:
                [data.append([timestamp, p["name"], p["pid"], float(p["CPU"]), float(p["RAM"]), float(p["RDISK"]), float(p["WDISK"])]) for p in jsondata[k]]
                    
            except Exception as error:
                print("No data structure found", error)

        df = cfg.pd.DataFrame(data, columns=["Timestamp", "Prname", "PID", "CPU", "RAM", "RDISK", "WDISK"])

        if(config["mode"] == 0):
            df = global_process(df)

        elif(config["mode"] == 1):
            df = by_pr_process(df)
        
        if(config["submode"] == 0):
            normal_parse(df, config["output_dir"])

        elif(config["submode"] == 1):
            advanced_parse(df, config["output_dir"], config["interval"])

def global_process(df):
    #esta parte es para el análisis general del equipo
    df = df.drop(["Prname", "PID"], axis=1)
    df = df.groupby("Timestamp").sum()
    df["Timestamp"] = df.index.values

    df_sh = df.shift(1)
        
    df["RDISK"] = (df["RDISK"] - df_sh["RDISK"]) / (df["Timestamp"] - df_sh["Timestamp"])
    df["WDISK"] = (df["WDISK"] - df_sh["WDISK"]) / (df["Timestamp"] - df_sh["Timestamp"])

    df.iat[0, 2] = 0
    df.iat[0, 3] = 0

    df = df.drop(["Timestamp"], axis=1)
    return df

def by_pr_process(df):

    df = df.groupby(["Prname", "PID"])
    dfs = []
    
    for (c1, c2), group in df:

        group_sh = group.shift(1)
        group["RDISK"] = (group["RDISK"] - group_sh["RDISK"]) / (group["Timestamp"] - group_sh["Timestamp"])
        group["WDISK"] = (group["WDISK"] - group_sh["WDISK"]) / (group["Timestamp"] - group_sh["Timestamp"])

        group.iat[0, 5] = 0
        group.iat[0, 6] = 0
        group = group.set_index('Timestamp')
        
        dfs.append(group)

    return dfs

def normal_parse(df, outputdir):
    if type(df) is list:    
        for prdf in df:
            dates = prdf.index.values
            instants = []

            for d in dates:
                date = cfg.datetime.fromtimestamp(d)
                instants.append(str(date.hour).zfill(2) + ":" + str(date.minute).zfill(2))
            
            prdf["Instant"] = instants
            
            name = prdf.iat[0, 0].replace("/", "-").replace("(", "").replace(")", "").replace(" ", "-").replace("_", "-")
            name = outputdir + name + "_" + prdf.iat[0, 1] + ".csv"
            prdf.to_csv(name, index=True)

    else:
        dates = df.index.values
        instants = []
        
        for d in dates:      
            date = cfg.datetime.fromtimestamp(d)
            instants.append(str(date.hour).zfill(2) + ":" + str(date.minute).zfill(2))

        df["Instant"] = instants
        
        name = outputdir + 'global_global.csv'
        df.to_csv(name, index=True)

def advanced_parse(df, outputdir, minterval):
    if type(df) is list:
        for prdf in df:
            get_data_stats(prdf, minterval, outputdir, 1)
    
    else:
        get_data_stats(df, minterval, outputdir, 0)

def get_data_stats(df, interval, outputdir, mode):
    if mode == 1:
        prname = df["Prname"].iloc[0]
        pid = df["PID"].iloc[0]
        df = df.drop(["Prname", "PID"], axis=1)

    dates = cfg.np.array([(cfg.datetime.fromtimestamp(d).hour * 60) + cfg.datetime.fromtimestamp(d).minute for d in df.index.values])

    ndf = cfg.pd.DataFrame()

    i = 0

    intervals = []
    minutes = 0
    while True:      
        intervals.append(minutes)
        minutes += interval

        if minutes > 1440:
            break

    for i in range(1, len(intervals)):
        indices = cfg.np.where((dates >= intervals[i - 1]) & (dates < intervals[i]))[0]
        
        if len(indices) > 0:
            adf = df.iloc[indices].mean().to_frame().T
            adf = adf.rename(columns={"CPU": "CPU (mean)", "RAM": "RAM (mean)", "RDISK": "RDISK (mean)", "WDISK": "WDISK (mean)"})
            
            adf = cfg.pd.merge(adf, df.iloc[indices].median().to_frame().T, left_index=True, right_index=True) 
            adf = adf.rename(columns={"CPU": "CPU (median)", "RAM": "RAM (median)", "RDISK": "RDISK (median)", "WDISK": "WDISK (median)"})
            
            adf = cfg.pd.merge(adf, df.iloc[indices].mode().iloc[0].to_frame().T, left_index=True, right_index=True)
            adf = adf.rename(columns={"CPU": "CPU (mode)", "RAM": "RAM (mode)", "RDISK": "RDISK (mode)", "WDISK": "WDISK (mode)"})

            adf = cfg.pd.merge(adf, df.iloc[indices].var().to_frame().T, left_index=True, right_index=True) 
            adf = adf.rename(columns={"CPU": "CPU (variance)", "RAM": "RAM (variance)", "RDISK": "RDISK (variance)", "WDISK": "WDISK (variance)"})
            
            d = str((intervals[i - 1] // 60) % 24).zfill(2) + ":" + str(intervals[i - 1] % 60).zfill(2) + "-" + str((intervals[i] // 60) % 24).zfill(2) + ":" + str(intervals[i] % 60).zfill(2)
            adf = cfg.pd.merge(adf, cfg.pd.DataFrame([d], columns=["Interval"]), left_index=True, right_index=True)

            ndf = cfg.pd.concat([ndf, adf], ignore_index = True) 
        
    if mode == 1:
        ndf["Prname"] = prname
        ndf["PID"] = pid
        
        name = prname.replace("/", "-").replace("(", "").replace(")", "").replace(" ", "-")
        name = outputdir + name + "_" + pid + ".csv"
        ndf.to_csv(name, index=False)
    
    else:
        name = outputdir + 'global_global.csv'
        ndf.to_csv(name, index=False)