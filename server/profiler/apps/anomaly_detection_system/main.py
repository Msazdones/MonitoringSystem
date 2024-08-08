import sys
sys.path.append('../shared/')

import config as cfg
import detector as det

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

            launcher_config.update({"model" : cfg.models_directory + launcher_config["alg"] + "/" + flist[int(opt_m2)]})
            launcher_config.update({"pr_target" : flist[int(opt_m2)].split("_")[2]})

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

            print("\n")
            opt_m2 = input("Now select the amount of samples that you want to use as observations each iteration, starting from the last record (integer): ")
            
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
                    det.detection(launcher_config, conn)
                    break
                elif opt_m2 == "n":
                    break

        if(opt_m1 == "2"):
            cfg.sys.exit()

if __name__ == "__main__":
    menu()