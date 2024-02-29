from pymongo import MongoClient
from itertools import islice
import os
import sys 
import time

#default config
def_data_dir = "./learning_and_detection/data_files/"
def_step = 1
def_samples = 20
def_output_model_dir = "./learning_and_detection/models/"
def_output_model_svm_dir = def_output_model_dir + "svm/"
csv_headers = "DATETIME,CPU,RAM,RDISK,WDISK,TOTALTIME"

path_to_svm_binary = "./learning_and_detection/SVM_profilerstandaloneApplication/run_SVM_profiler.sh"
path_to_iforest_binary = "./learning_and_detection/iforest_profilerstandaloneApplication/run_iforest_profiler.sh"
matlab_dependencies = "/usr/local/MATLAB/R2023b/"

def connect_to_db():
    client = MongoClient("mongodb://127.0.0.1:27017/")
    return client["test"]

def parse_file_to_detection():
    pass

def train_model(config):
    if(config["alg"] == "svm"):
        binary = path_to_svm_binary
    elif(config["alg"] == "svm"):
        binary = path_to_iforest_binary
    
    for i in config["input_data"]:
        execution = binary + " " + matlab_dependencies + " " + config["input_dir"] + i + " " + config["output_dir"]
        print(execution)
        os.system(execution)

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
        print(len(dates), cnt)
        if(len(dates) == 0):
            continue
            
        for k in dates:
            try:
                for p in jsondata[k]:    
                    csv_info = str(k) + "," + str(p["CPU"]) + "," + str(p["RAM"]) + "," + str(p["RDISK"]) + "," + str(p["WDISK"]) + "," + str(p["TOTALTIME"]) + "\n"
                    csv_file = config["output_dir"] + p["name"].replace("/", "-") + ".csv"
                    
                    if(not os.path.isfile(csv_file)):
                        csv_info  = csv_headers + "\n" + csv_info

                    f = open(csv_file, "a")
                    f.write(csv_info)
                    f.close()
            except Exception as error:
                print("No data structure found", error)

def get_db_info(db_conn):
   return db_conn.list_collection_names()

def check_numeric_input(i, ll, hl):
    if (not i.isnumeric()):
        return False
    
    ii = int(i)
    if ((ii < ll) or (ii > hl)):
        return False
    
    return True

def print_choosing_list(l):
    col = 0
    i = 0
    for c in l:
        cadena = "(" + str(i) + ") " + c
        print(cadena + " " * (60 - (len(cadena))),  end="")
        i = i + 1
        if col == 3:
            print() 
            col = 0
        else:
            col = col + 1 

def menu():
    parse_config = {"clients" : [], "samples" : def_samples, "step" : def_step, "output_dir" : def_data_dir}
    training_config = {"alg" : "svm", "input_dir" : def_data_dir, "input_data" : "", "output_dir" : def_output_model_svm_dir}
    while True:
        print("Welcome to the machine learning model training module. What do you want to do?\n")
        print("     1. Parse data from database.")
        print("     2. Train model.")
        print("     3. Help.")
        print("     4. Exit.\n")

        opt_m1 = input("Choose an option (integer 1-4): ")
        print("\n")
        
        if(not check_numeric_input(opt_m1, 1, 4)):
            print("Bad input. Try again.")
            print("\n")
            continue

        if(opt_m1 == "1"):
            conn = connect_to_db()
            clients = get_db_info(conn)
            parse_config.update({"clients" : clients})

            while True:
                print("You want to parse the data from de database, you are now connected. Choose your option:")
                print("     1. Configure and start process.")
                print("     2. Check current configuration.")
                print("     3. Start process.")
                print("     4. Back.\n")

                opt_m2 = input("Choose an option (integer 1-4): ")
                print("\n")

                if(not check_numeric_input(opt_m2, 1, 4)):
                    print("Bad input. Try again.")
                    print("\n")
                    continue

                if(opt_m2 == "1"):
                    print("Aviable clients: \n")

                    print_choosing_list(clients)

                    print("\n")
                    opt_m2 = input("Choose one or more, separated by space (integer 0-" + str(len(clients)-1) + ", or type all for all the clients): ")
                    
                    if(opt_m2 == "all"):
                        client_target = clients
                    
                    elif(check_numeric_input(opt_m2, 0, len(clients)-1)):
                        client_target=[]
                        
                        for i in opt_m2:
                            client_target.append(clients[int(i)])
                    
                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue  
                    
                    parse_config.update({"clients" : client_target})

                    print("\n")
                    opt_m2 = input("Now select the amount of samples the you want to parse, starting from the last record (integer, type all for all samples, or press intro for default (" + str(def_samples) + ")): ")

                    if(opt_m2 == "all"):
                        parse_config.update({"samples" : "all"})
                   
                    elif(opt_m2 == ''):
                        parse_config.update({"samples" : def_samples})
                    
                    elif(opt_m2.isnumeric()):
                        parse_config.update({"samples" : int(opt_m2)})

                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue  

                    print("\n")
                    opt_m2 = input("Now select the step that you want to de decimating process (1 = None) (integer, or press intro for default (" + str(def_step) + ")): ")

                    if(opt_m2 == ''):
                        parse_config.update({"step" : def_step})
                    
                    elif(opt_m2.isnumeric()):
                        parse_config.update({"step" : int(opt_m2)})

                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue  

                    print("\n")
                    opt_m2 = input("Now select the output directory (string, or press intro for default (" + def_data_dir + ")): ")

                    if(opt_m2 == ''):
                        parse_config.update({"output_dir" : def_data_dir})

                    elif(os.path.isdir(opt_m2)):
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

                if(not check_numeric_input(opt_m2, 1, 4)):
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
                    opt_m2 = input("Now select the input directory (press intro for default (" + def_data_dir + ")): ")

                    if(opt_m2 == ''):
                        flist = os.listdir(def_data_dir)
                        training_config.update({"input_dir" : def_data_dir})

                    elif(os.path.isdir(opt_m2)):
                        flist = os.listdir(opt_m2)
                        training_config.update({"input_dir" : opt_m2})
                    
                    else:
                        print("Bad input. Try again.")
                        print("\n")
                        continue 

                    print_choosing_list(flist)
                    print("\n")
                    opt_m2 = input("Choose one or more, separated by space (integer 0-" + str(len(flist)-1) + ", or type all for all the files): ")
                    
                    if(opt_m2 == "all"):
                        target_files = flist
                    
                    else:
                        fl = opt_m2.split(" ")
                        fl = list(set([f for f in fl if f]))

                        target_files=[]
                        for f in fl:
                            if(check_numeric_input(f, 0, len(flist)-1)):
                                target_files.append("'" + flist[int(f)] + "'")

                            else:
                                print("Bad input. Try again.")
                                print("\n")
                                continue
                                
                    training_config.update({"input_data" : target_files})
                    print("\n")
                    opt_m2 = input("Now select the output directory (press intro for default (" + str(def_output_model_dir) + training_config["alg"] + ")): ")

                    if(opt_m2 == ''):
                        training_config.update({"output_dir" : str(def_output_model_dir) + training_config["alg"] + "/"})

                    elif(os.path.isdir(opt_m2)):
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
                            train_model(training_config)
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
                            train_model(training_config, conn)
                            break
                        elif opt_m2 == "n":
                            break

                elif(opt_m2 == "4"):
                    break

        elif(opt_m1 == "3"):
            pass
        elif(opt_m1 == "4"):
            print("Exiting.")
            sys.exit()
    


if __name__ == "__main__":
    menu()