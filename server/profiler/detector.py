import config as cfg
import chardet 

def parse_file_to_detection(config, conn):

    for host in config["clients"]:
        rawdata = reversed(list(conn[host].find({},{"_id": 0}).sort({"_id": -1}).limit(config["samples"])))

        data = {}
        for d in rawdata:
            data.update(d)

        dates = list(data.keys())

        if(len(dates) == 0):
            continue

        pid_lists = {}
        for k in dates:
            for p in data[k]:
                if(p["name"] == config["pr_target"]):
                    if(p["pid"] not in pid_lists):
                        pid_lists.update({p["pid"] : ""})

                    timestamp = str(int(cfg.datetime.strptime(str(k), "%Y-%m-%d %H:%M:%S").timestamp()))
                    csv_info = timestamp + "," + str(p["CPU"]) + "," + str(p["RAM"]) + "," + str(p["RDISK"]) + "," + str(p["WDISK"]) + "," + str(p["TOTALTIME"]) + "\n"
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
            '" "' + str(len(config["clients"])) +\
            '" "' + str(config["period"]) + '"'

    print(execution)
    proceso = cfg.subprocess.Popen(execution, shell=True)

def log_detection_results(samples, pids, rdata):
        ts = []
        rt = []
        st = []

        for i in range(0, len(pids)):
            ll = samples * i
            hl = samples * (i + 1)
            ts.append(rdata[ll:hl])

            ll = samples * (i + len(pids))
            hl = samples * (i + len(pids) + 1)
            rt.append(rdata[ll:hl])

            ll = samples * (i + (len(pids) * 2))
            hl = samples * (i + (len(pids) * 2) + 1)
            st.append(rdata[ll:hl])
        
        for i in range(0, len(pids)):
            print(pids[i])
            for j in range(0, len(st[i])):
                if st[i][j] == '1':
                    print("Alerta, positivo:", ts[i][j], rt[i][j], st[i][j])
                else:
                    print("Todo chill", ts[i][j], rt[i][j], st[i][j])
        print("----------------------------------------------------------------")

def detection(config, conn):
    ssocket = cfg.socket.socket(cfg.socket.AF_INET, cfg.socket.SOCK_STREAM)
    ssocket.bind(('localhost', 6112))
    ssocket.listen(1)

    launch_detector_matlab(config)

    sclient, client_address = ssocket.accept()

    while True:
        cd = parse_file_to_detection(config, conn)
        pids = list(cd.keys())
        
        if len(pids) != 0:
            payload = ""
            for k in pids:
                payload = payload + cd[k]
            payload = payload[0:len(payload)-1]

            sclient.send(payload.encode())
            s = sclient.recv(1000)
            rdata = sclient.recv(int(s.decode()), cfg.socket.MSG_WAITALL)
            rdata = list(filter(None, rdata.decode().split(" ")))
            
            log_detection_results(config["samples"], pids, rdata)

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
            opt_m2 = input("Choose one or more, separated by space (integer 0-" + str(len(clients)-1) + ", or type all for all the clients): ")
            
            if(opt_m2 == "all"):
                client_target = clients
            
            elif(cfg.aux.check_numeric_input(opt_m2, 0, len(clients)-1)):
                client_target=[]
                
                for i in opt_m2:
                    client_target.append(clients[int(i)])
            
            else:
                print("Bad input. Try again.")
                print("\n")
                continue  
            
            launcher_config.update({"clients" : client_target})
            
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