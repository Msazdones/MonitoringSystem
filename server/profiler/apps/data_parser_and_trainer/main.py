import sys
sys.path.append('../shared/')

import config as cfg
import data_parser as dp
import model_trainer as mt

def menu():
    parse_config = {"clients" : [], "samples" : cfg.def_samples, "step" : cfg.def_step, "output_dir" : cfg.def_normal_data_dir}
    training_config = {"alg" : "svm", "input_dir" : cfg.def_normal_data_dir, "input_data" : "", "output_dir" : cfg.def_output_model_svm_dir}
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
                print("You want to parse the data from the database, you are now connected. Choose your option:")
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
                    opt_m2 = input("Now select the step that you want to the decimating process (1 = None) (integer, or press intro for default (" + str(cfg.def_step) + ")): ")

                    if(opt_m2 == ''):
                        parse_config.update({"step" : cfg.def_step})
                    
                    elif(cfg.aux.check_numeric_input(opt_m2, 1, "-")):
                        parse_config.update({"step" : int(opt_m2)})

                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue  

                    print("\n")
                    opt_m2 = input("Now select the parse mode (0 = global, 1 = by process): ")

                    if(cfg.aux.check_numeric_input(opt_m2, 0, 1)):
                        parse_config.update({"mode" : int(opt_m2)})

                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue

                    print("\n")
                    opt_m2 = input("Now select the parse submode (0 = classic, 1 = advanced): ")

                    if(cfg.aux.check_numeric_input(opt_m2, 0, 1)):
                        parse_config.update({"submode" : int(opt_m2)})
                    
                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue 

                    if(parse_config["submode"] == 1):
                        print("\n")
                        opt_m2 = input("Now select the advanced parse interval (positive integer, in minutes): ")
                        
                        if(cfg.aux.check_numeric_input(opt_m2, 0, 1000000000)):
                            parse_config.update({"interval" : int(opt_m2)})
                        
                        else:
                            print("Bad input. Try again.")
                            print("\n")
                            continue 
                    
                    if(parse_config["submode"] == 0):
                        ddir = cfg.def_normal_data_dir
                    
                    elif(parse_config["submode"] == 1):    
                        ddir = cfg.def_advanced_data_dir
                    
                    print("\n")
                    opt_m2 = input("Now select the output directory (string, or press intro for default (" + ddir + ")): ")

                    if(opt_m2 == ''):
                        parse_config.update({"output_dir" : ddir})

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
                            dp.parse_file_for_training(parse_config, conn)
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
                            dp.parse_file_for_training(parse_config, conn)
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
                    opt_m2 = input("Now select the parse mode (0 = classic, 1 = advanced): ")

                    if(cfg.aux.check_numeric_input(opt_m2, 0, 1)):
                        training_config.update({"mode" : int(opt_m2)})
                    
                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue 

                    if(training_config["mode"] == 0):
                        ddir = cfg.def_normal_data_dir
                    
                    elif(training_config["mode"] == 1):    
                        ddir = cfg.def_advanced_data_dir
                    
                    print("\n")
                    opt_m2 = input("Now select the output directory (string, or press intro for default (" + ddir + ")): ")

                    if(opt_m2 == ''):
                        flist = cfg.os.listdir(ddir)
                        training_config.update({"input_dir" : ddir})

                    elif(cfg.os.path.isdir(opt_m2)):
                        flist = cfg.os.listdir(opt_m2)
                        training_config.update({"input_dir" : opt_m2})
                    
                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue 
                    
                    tpl = cfg.aux.print_pr_options(flist)

                    print("\n")
                    opt_m2 = input("Choose one or more, separated by space (integer 0-" + str(len(tpl)-1) + "). You must select the pids that you want, or type all (example: 1 (24,36,2874) 2 (all)... ): ")
                    
                    dat = opt_m2.split(" ")
                    prs = dat[0::2]
                    pids = dat[1::2]

                    #381 (14) 310 (351386,259238) 379 (all) | 8 (all) 148 (global)
                    target_files = []

                    try:                    
                        for p in range(0, len(prs)):
                            if(cfg.aux.check_numeric_input(prs[p], 0, len(tpl)-1)):
                                pidl = pids[p][1:len(pids[p])-1].split(",")

                                prl = []
                                for i in pidl:
                                    if(i == "all"):
                                        for j in tpl[int(prs[p])][1]:

                                            if j == "all":
                                                continue

                                            name = tpl[int(prs[p])][0] + "_" + j + ".csv"
                                            prl.append(name)

                                    elif(i in tpl[int(prs[p])][1]):
                                        name = tpl[int(prs[p])][0] + "_" + i + ".csv"
                                        prl.append(name)

                                    else:
                                        raise ValueError('Pid not found.')
                                target_files.append(prl)
                                
                            else:
                                raise ValueError('Input error.')   
                    
                    except:
                        continue
                                
                    training_config.update({"input_data" : target_files})
                    
                    if(training_config["mode"] == 0):
                        print("\n")
                        opt_m2 = input("Now select what type(s) of data you want to use for training, one or more separated by space (CPU, RAM, RDISK, WDISK or all): ")
                        
                        allowed_nh = cfg.normal_csv_headers.split(",")
                        if(opt_m2 == "all"):
                            training_config.update({"datatype" :allowed_nh})
                        else:
                            dt = opt_m2.split(" ")
                            status = True
                            for d in dt:
                                if d not in allowed_nh:
                                    status = False
                                    break
                            if status == False:
                                print("Bad input. Try again.")
                                print("\n")
                                continue
                            else: 
                                training_config.update({"datatype" : dt})

                    elif(training_config["mode"] == 1):
                        print("\n")
                        opt_m2 = input("Now select what type(s) of data you want to use for training, one or more separated by space and specify the exact metrics. (Example: CPU (mean,median,mode,variance) RAM (mean) RDISK (all)...): ")                                
                        
                        headers = opt_m2.split(" ")
                        groups = headers[0::2]
                        metrics = headers[1::2]

                        status = True
                        allowed_ah = cfg.advanced_csv_headers.split(",")
                        allowed_nh = cfg.normal_csv_headers.split(",")
                        selected_h = []

                        for i in range(0, len(groups)):
                            if groups[i] in allowed_nh:
                                mets = metrics[i].replace("(", "").replace(")", "").split(",")
                                
                                for m in mets:
                                    h = groups[i] + " (" + m + ")"

                                    if m == "all":
                                        for am in cfg.all_metrics:
                                            selected_h.append(groups[i] + " (" + am + ")")

                                    elif h in allowed_ah:
                                        selected_h.append(h)
                                    
                                    else:
                                        status = False
                                
                                #CPU (MEAN,MODE,MEDIAN,VARIANCE) RAM (all) WDISK (MEAN,VARIANCE)
                            else:
                                status = False
                        
                        if status == False:
                            print("Bad input. Try again.")
                            print("\n")
                            continue
                            
                        else:
                            training_config.update({"datatype" : selected_h})

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
                            mt.train_model(training_config)
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
                            mt.train_model_matlab(training_config)
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