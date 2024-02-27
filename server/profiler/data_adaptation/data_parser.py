from pymongo import MongoClient
from itertools import islice
from os import path
import sys 
import time

dat_dir = "./learning_and_detection/data_files/"

def connect_to_db():
    client = MongoClient("mongodb://127.0.0.1:27017/")
    return client["test"]

def check_input(params):
    step = 1
    clientid = None

    if(len(params) <= 3 and (len(params) >= 1)):
        if(len(params) > 0):
            if(not path.isdir(params[0])):
                print("Error: The first parameter must be a directory. Exiting.")
                print("python3 train_model.py <savedir> [step] [clientid]")
                sys.exit()  

            data_dir = params[0]

        if(len(params) > 1):
            if(not params[1].isdigit()):
                print("Error: The step arg must be an integer")
                print("python3 train_model.py <savedir> [step] [clientid]")
                sys.exit()

            try:
                step = int(params[1])
            except:
                print("Error: The step arg must be an integer")
                print("python3 train_model.py <savedir> [step] [clientid]")
                sys.exit()           
        
        if(len(params) == 3):
            clientid = "Client_" + params[2]
    return data_dir, step, clientid

def main():
    data_dir, step, clientid = check_input(sys.argv[1:len(sys.argv)])
    print(data_dir, step, clientid)

    db_conn = connect_to_db()
    hlist = db_conn.list_collection_names()
    
    if(clientid != None):
        clindex = hlist.index(clientid)
        hlist = [hlist[clindex]]

    for host in hlist:
        jsondata = {}
        dates = []
        rawdata = db_conn[host].find({},{"_id": 0})

        stepcnt = step - 1 #para quedarnos siempre con la primera muestra
        cnt = 0
        for d in rawdata:
            cnt = cnt +1 
            if(stepcnt == step-1): 
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
                    csv_file = data_dir + p["name"].replace("/", "-") + "_" + p["pid"] + ".csv"
        
                    f = open(csv_file, "a")
                    f.write(csv_info)
                    f.close()
            except Exception as error:
                print("No data structure found", error)            

if __name__ == "__main__":
	main()