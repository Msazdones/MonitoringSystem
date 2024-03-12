import config as cfg

def train_model_matlab(config):
    
    cfg.os.environ["LD_LIBRARY_PATH"] = ""
    for d in cfg.matlab_dependencies:
        cfg.os.environ["LD_LIBRARY_PATH"] += cfg.matlab_dependencies_root + d + cfg.os.pathsep

    if(config["alg"] == "svm"):
        binary = cfg.path_to_svm_binary
    elif(config["alg"] == "svm"):
        binary = cfg.path_to_iforest_binary
    
    for i in config["input_data"]:
        execution = 'eval ' + '"' + binary + '"' + ' "' + config["input_dir"] + i + '" "' + config["output_dir"] + '"'
        print(execution)
        cfg.os.system(execution)

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
            
        for k in dates:
            try:
                for p in jsondata[k]:    
                    timestamp = str(int(cfg.datetime.strptime(str(k), "%Y-%m-%d %H:%M:%S").timestamp()))
                    csv_info = timestamp + "," + str(p["CPU"]) + "," + str(p["RAM"]) + "," + str(p["RDISK"]) + "," + str(p["WDISK"]) + "," + str(p["TOTALTIME"]) + "\n"
                    csv_file = config["output_dir"] + p["name"].replace("/", "-") + ".csv"
                    
                    if(not cfg.os.path.isfile(csv_file)):
                        csv_info  = cfg.csv_headers + "\n" + csv_info

                    f = open(csv_file, "a")
                    f.write(csv_info)
                    f.close()
            except Exception as error:
                print("No data structure found", error)

def menu():
    parse_config = {"clients" : [], "samples" : cfg.def_samples, "step" : cfg.def_step, "output_dir" : cfg.def_data_dir}
    training_config = {"alg" : "svm", "input_dir" : cfg.def_data_dir, "input_data" : "", "output_dir" : cfg.def_output_model_svm_dir}
    conn = cfg.aux.connect_to_db()
    
    while True:
        print("Welcome to the machine learning model training module. What do you want to do?\n")
        print("     1. Parse data from database.")
        print("     2. Train model.")
        print("     3. Help.")
        print("     4. Exit.\n")

        opt_m1 = input("Choose an option (integer 1-4): ")
        print("\n")
        
        if(not cfg.aux.check_numeric_input(opt_m1, 1, 4)):
            print("Bad input. Try again.")
            print("\n")
            continue

        if(opt_m1 == "1"):
            clients = cfg.aux.get_db_info(conn)
            parse_config.update({"clients" : clients})

            while True:
                print("You want to parse the data from de database, you are now connected. Choose your option:")
                print("     1. Configure and start process.")
                print("     2. Check current configuration.")
                print("     3. Start process.")
                print("     4. Back.\n")

                opt_m2 = input("Choose an option (integer 1-4): ")
                print("\n")

                if(not cfg.aux.check_numeric_input(opt_m2, 1, 4)):
                    print("Bad input. Try again.")
                    print("\n")
                    continue

                if(opt_m2 == "1"):
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
                    
                    parse_config.update({"clients" : client_target})

                    print("\n")
                    opt_m2 = input("Now select the amount of samples the you want to parse, starting from the last record (integer, type all for all samples, or press intro for default (" + str(cfg.def_samples) + ")): ")

                    if(opt_m2 == "all"):
                        parse_config.update({"samples" : "all"})
                   
                    elif(opt_m2 == ''):
                        parse_config.update({"samples" : cfg.def_samples})
                    
                    elif(cfg.aux.check_numeric_input(opt_m2, 1, "-")):
                        parse_config.update({"samples" : int(opt_m2)})

                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue  

                    print("\n")
                    opt_m2 = input("Now select the step that you want to de decimating process (1 = None) (integer, or press intro for default (" + str(cfg.def_step) + ")): ")

                    if(opt_m2 == ''):
                        parse_config.update({"step" : cfg.def_step})
                    
                    elif(cfg.aux.check_numeric_input(opt_m2, 1, "-")):
                        parse_config.update({"step" : int(opt_m2)})

                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue  

                    print("\n")
                    opt_m2 = input("Now select the output directory (string, or press intro for default (" + cfg.def_data_dir + ")): ")

                    if(opt_m2 == ''):
                        parse_config.update({"output_dir" : cfg.def_data_dir})

                    elif(cfg.os.path.isdir(opt_m2)):
                        parse_config.update({"output_dir" : opt_m2})
                    
                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue  

                    print("\n")
                    print("The current configuration is: ", parse_config)
                    print("Do you want to start the process now?")
                    while True:
                        opt_m2 = input("y/n: ")
                        if opt_m2 == "y":
                            parse_file_for_training(parse_config, conn)
                            break
                        elif opt_m2 == "n":
                            break

                elif(opt_m2 == "2"):
                    print("\n")
                    print("Current configuration: ", parse_config)

                elif(opt_m2 == "3"):
                    print("\n")
                    print("The current configuration is: ", parse_config)
                    
                    while True:
                        opt_m2 = input("y/n: ")
                        if opt_m2 == "y":
                            parse_file_for_training(parse_config, conn)
                            break
                        elif opt_m2 == "n":
                            break

                elif(opt_m2 == "4"):
                    break

        elif(opt_m1 == "2"):
            while True:
                print("You want to train a machine learning model. Choose your option:")
                print("     1. Configure and start process.")
                print("     2. Check current configuration.")
                print("     3. Start process.")
                print("     4. Back.\n")

                opt_m2 = input("Choose an option (integer 1-4): ")
                print("\n")

                if(not cfg.aux.check_numeric_input(opt_m2, 1, 4)):
                    print("Bad input. Try again.")
                    print("\n")
                    continue

                if(opt_m2 == "1"):

                    opt_m2 = input("Choose the algorithm (svm or iforest): ")
                    
                    if(opt_m2 == "svm"):
                        training_config.update({"alg" : "svm"})
                    
                    elif(opt_m2 == "iforest"):
                        training_config.update({"alg" : "iforest"})

                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue  

                    print("\n")
                    opt_m2 = input("Now select the input directory (press intro for default (" + cfg.def_data_dir + ")): ")

                    if(opt_m2 == ''):
                        flist = cfg.os.listdir(cfg.def_data_dir)
                        training_config.update({"input_dir" : cfg.def_data_dir})

                    elif(cfg.os.path.isdir(opt_m2)):
                        flist = cfg.os.listdir(opt_m2)
                        training_config.update({"input_dir" : opt_m2})
                    
                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue 

                    cfg.aux.print_options(flist)
                    print("\n")
                    opt_m2 = input("Choose one or more, separated by space (integer 0-" + str(len(flist)-1) + ", or type all for all the files): ")
                    
                    if(opt_m2 == "all"):
                        target_files = flist
                    
                    else:
                        fl = opt_m2.split(" ")
                        fl = list(set([f for f in fl if f]))

                        target_files=[]
                        for f in fl:
                            if(cfg.aux.check_numeric_input(f, 0, len(flist)-1)):
                                target_files.append("'" + flist[int(f)] + "'")

                            else:
                                print("Bad input. Try again.")
                                print("\n")
                                continue
                                
                    training_config.update({"input_data" : target_files})
                    print("\n")
                    opt_m2 = input("Now select the output directory (press intro for default (" + str(cfg.def_output_model_dir) + training_config["alg"] + ")): ")

                    if(opt_m2 == ''):
                        training_config.update({"output_dir" : str(cfg.def_output_model_dir) + training_config["alg"] + "/"})

                    elif(cfg.os.path.isdir(opt_m2)):
                        training_config.update({"output_dir" : opt_m2})
                    
                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue 

                    print("\n")
                    print("The current configuration is: ", training_config)
                    print("Do you want to start the process now?")
                    while True:
                        opt_m2 = input("y/n: ")
                        if opt_m2 == "y":
                            train_model_matlab(training_config)
                            break
                        elif opt_m2 == "n":
                            break

                elif(opt_m2 == "2"):
                    print("\n")
                    print("Current configuration: ", training_config)

                elif(opt_m2 == "3"):
                    print("\n")
                    print("The current configuration is: ", training_config)

                    if(training_config["input_data"] == ""):
                        print("\n")
                        print("You must select the input data. Please, use the configuration option.")
                        continue

                    while True:
                        opt_m2 = input("y/n: ")
                        if opt_m2 == "y":
                            train_model_matlab(training_config)
                            break
                        elif opt_m2 == "n":
                            break

                elif(opt_m2 == "4"):
                    break

        elif(opt_m1 == "3"):
            pass
        elif(opt_m1 == "4"):
            print("Exiting.")
            cfg.sys.exit()
    


if __name__ == "__main__":
    menu()