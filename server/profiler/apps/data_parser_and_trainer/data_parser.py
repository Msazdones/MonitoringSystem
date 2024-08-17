import config as cfg

def parse_file_for_training(config, db_conn):
    for host in config["clients"]:
        jsondata = []
        
        #esto hay que revisarlo que funciona regular ahora con los cambios realizados
        if(config["samples"] == "all"):
            rawdata = db_conn[host].find({"label": {"$in": config["labels"]}},{"_id": 0})

        else:
            rawdata = reversed(list(db_conn[host].find({"label": {"$in": config["labels"]}},{"_id": 0}).sort({"_id": -1}).limit(config["samples"])))

        stepcnt = config["step"] - 1 #para quedarnos siempre con la primera muestra
        cnt = 0
        for d in rawdata:
            jsondata.append(d)

        if(len(jsondata) == 0):
            continue
        
        data = []
        # revisar esto para optimizarlo

        for jd in jsondata:
            date = cfg.datetime.strptime(str(jd["date"]), "%Y-%m-%d %H:%M:%S")
            timestamp = int(date.timestamp())

            data.append([timestamp, jd["name"], jd["data"]["pid"], float(jd["data"]["CPU"]), float(jd["data"]["RAM"]), float(jd["data"]["RDISK"]), float(jd["data"]["WDISK"])])

        df = cfg.pd.DataFrame(data, columns=["Timestamp", "Prname", "PID", "CPU", "RAM", "RDISK", "WDISK"])
        df = df.sort_values(["Timestamp"])

        if(config["mode"] == 0):
            df = global_process(df)

        elif(config["mode"] == 1):
            df = by_pr_process(df)
        
        if(config["submode"] == 0):
            normal_parse(df, config)

        elif(config["submode"] == 1):
            advanced_parse(df, config)

def global_process(df):
    df = cfg.aux.process_R_and_W(df)
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

def normal_parse(df, config):
    if type(df) is list:    
        for prdf in df:
            dates = prdf.index.values
            instants = []

            for d in dates:
                date = cfg.datetime.fromtimestamp(d)
                instants.append(str(date.hour).zfill(2) + ":" + str(date.minute).zfill(2))
            
            prdf["Instant"] = instants
            
            name = prdf.iat[0, 0].replace("/", "-").replace("(", "").replace(")", "").replace(" ", "-").replace("_", "-")
            try:
                name = config["output_dir"] + config["labels"][0] + "_" + name + "_" + prdf.iat[0, 1] + ".csv"
                prdf.to_csv(name, index=True)
            except:
                pass

    else:
        dates = df.index.values
        instants = []
        
        for d in dates:      
            date = cfg.datetime.fromtimestamp(d)
            instants.append(str(date.hour).zfill(2) + ":" + str(date.minute).zfill(2))

        df["Instant"] = instants
        
        name = config["output_dir"] + config["labels"][0] + '_global_global.csv'
        df.to_csv(name, index=True)

def advanced_parse(df, config):
    if type(df) is list:
        for prdf in df:
            ndf, prinfo = cfg.aux.get_data_stats(prdf, config["interval"], 1)
            save_to_csv(ndf, prinfo, config, 1)

    else:
        ndf = cfg.aux.get_data_stats(df, config["interval"], 0)
        save_to_csv(ndf, (), config, 0)

def save_to_csv(ndf, prinfo, config, mode):
    if mode == 1:
        ndf["Prname"] = prinfo[0]
        ndf["PID"] = prinfo[1]
        
        name = prinfo[0].replace("/", "-").replace("(", "").replace(")", "").replace(" ", "-")
        try:
            name = config["output_dir"] + config["labels"][0] + "_" +name + "_" + prinfo[1] + ".csv"
            ndf.to_csv(name, index=False)
        
        except:
            pass
    
    else:
        name = config["output_dir"] + config["labels"][0] + '_global_global.csv'
        ndf.to_csv(name, index=False)