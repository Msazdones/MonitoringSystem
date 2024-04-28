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
    for k in dates:
        for p in data[k]:
            if(p["name"] == config["pr_target"]):
                if(p["pid"] not in pid_lists):
                    pid_lists.update({p["pid"] : ""})

                timestamp = str(int(cfg.datetime.strptime(str(k), "%Y-%m-%d %H:%M:%S").timestamp()))
                csv_info = timestamp 
                for c in config["datatype"]:
                    csv_info = csv_info + "," +  str(p[c])
                
                csv_info = csv_info + "\n"
                pid_lists.update({p["pid"] : pid_lists[p["pid"]] + csv_info})             
    
    return pid_lists


def launch_detector_matlab(config):
    cfg.os.environ["LD_LIBRARY_PATH"] = ""
    for d in cfg.matlab_dependencies:
        cfg.os.environ["LD_LIBRARY_PATH"] += cfg.matlab_dependencies_root + d + cfg.os.pathsep

    binary = cfg.path_to_detector_binary

    execution = 'eval ' + \
            '"' + binary +\
            '" "' + config["model"] +\
            '" "' + config["alg"] +\
            '" "' + ",".join(config["datatype"]) +\
            '" "' + str(config["period"]) + '"'

    print(execution)
    proceso = cfg.subprocess.Popen(execution, shell=True)

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
    ssocket = cfg.socket.socket(cfg.socket.AF_INET, cfg.socket.SOCK_STREAM)
    ssocket.bind(('localhost', 6112))
    ssocket.listen(1)

    launch_detector_matlab(config)

    sclient, client_address = ssocket.accept()

    logfile = create_log_file(config["pr_target"])

    while True:
        cd = parse_file_to_detection(config, conn)
        pids = list(cd.keys())
        
        if len(pids) != 0 or cd == {}:
            payload = ""
            for k in pids:
                payload = payload + cd[k]
            payload = payload[0:len(payload)-1]

            sclient.send(payload.encode())
            s = sclient.recv(1000)
            rdata = sclient.recv(int(s.decode()), cfg.socket.MSG_WAITALL)
            rdata = list(filter(None, rdata.decode().split(" ")))
            
            log_detection_results(rdata, cd, config["alg"], logfile)

        else:
            print("De momento no hay muestras.")
            cfg.time.sleep(config["period"])


#{"alg", "model", "clients", "samples", "period", "pr_target"} 4683

def menu():
    launcher_config = {}
    conn = cfg.aux.connect_to_db()

    while True:
        print("Welcome to the detector launcher. What do you want to do?\n")
        print("     1. Configure and launch.")
        print("     2. Exit.\n")

        opt_m1 = input("Choose an option (integer 1-2): ")
        print("\n")
        
        if(not cfg.aux.check_numeric_input(opt_m1, 1, 2)):
            print("Bad input. Try again.")
            print("\n")
            continue

        if(opt_m1 == "1"):

            opt_m2 = input("Choose the algorithm (svm or iforest): ")
            
            if(opt_m2 == "svm"):
                launcher_config.update({"alg" : "svm"})
            
            elif(opt_m2 == "iforest"):
                launcher_config.update({"alg" : "iforest"})

            else:
                print("Bad input. Try again.")
                print("\n")
                continue  

            flist = cfg.os.listdir(cfg.models_directory + launcher_config["alg"])
            cfg.aux.print_options(flist)
            print("\n")

            opt_m2 = input("Choose your machine learning model (just one) for detection, from directory '" + cfg.models_directory + launcher_config["alg"] + "/' (integer): ")
            
            if(not cfg.aux.check_numeric_input(opt_m2, 0, len(flist)-1)):
                print("Bad input. Try again.")
                print("\n")
                continue

            launcher_config.update({"model" : cfg.models_directory + launcher_config["alg"] + "/'" + flist[int(opt_m2)] + "'"})
            launcher_config.update({"pr_target" : cfg.re.findall("\(.*\)", flist[int(opt_m2)])[0]})

            clients = cfg.aux.get_db_info(conn)
            print("Aviable clients: \n")

            cfg.aux.print_options(clients)

            print("\n")
            opt_m2 = input("Choose one client (integer 0-" + str(len(clients)-1) + "): ")
            
            if(not cfg.aux.check_numeric_input(opt_m2, 0, len(clients)-1)):
                print("Bad input. Try again.")
                print("\n")
                continue       

            
            launcher_config.update({"clients" : clients[int(opt_m2)]})
            
            opt_m2 = input("Now select what type(s) of data you want to use for training, one or more separated by space (CPU, RAM, RDISK, WDISK or all): ")
            print("\n")

            if(opt_m2 == "all"):
                launcher_config.update({"datatype" : ["CPU", "RAM", "RDISK", "WDISK"]})
            else:
                dt = opt_m2.split(" ")
                status = True
                for d in dt:
                    if d not in ["CPU", "RAM", "RDISK", "WDISK"]:
                        status = False
                        break
                if status == False:
                    print("Bad input. Try again.")
                    print("\n")
                    continue
                else: 
                    launcher_config.update({"datatype" : dt})

            print("\n")
            opt_m2 = input("Now select the amount of samples the you want to use as observations each iteration, starting from the last record (integer): ")
            
            if(cfg.aux.check_numeric_input(opt_m2, 1, "-")):
                launcher_config.update({"samples" : int(opt_m2)})

            else:
                print("Bad input. Try again.")
                print("\n")
                continue  

            print("\n")
            opt_m2 = input("Now select the period of the detection process (float, or type none for no period): ")
            
            if(opt_m2 == "none"):
                launcher_config.update({"period" : "none"})
            
            elif(cfg.aux.check_float_input(opt_m2, 1, "-")):
                launcher_config.update({"period" : float(opt_m2)})

            else:
                print("Bad input. Try again.")
                print("\n")
                continue  

            print("The current configuration is: ", launcher_config)
            print("Do you want to start the process now?")
            while True:
                opt_m2 = input("y/n: ")
                if opt_m2 == "y":
                    detection(launcher_config, conn)
                    break
                elif opt_m2 == "n":
                    break

        if(opt_m1 == "2"):
            cfg.sys.exit()

if __name__ == "__main__":
    menu()