from pymongo import MongoClient
from itertools import islice
import sys 
import time

dat_dir = "./dat_files/"

def connect_to_db():
    client = MongoClient("mongodb://127.0.0.1:27017/")
    return client["test"]

def main():
    step = 1
    if(len(sys.argv) > 2):
        print("Error: Max number of args exceeded. Exiting.")
        sys.exit()
    elif(len(sys.argv) == 1):
        pass
    elif(not sys.argv[1].isdigit()):
        print("Error: The step arg must be an integer")
        sys.exit()
    else:
        try:
            step = int(sys.argv[1])
        except:
            print("Error: The step arg must be an integer")
            sys.exit()
    
    db_conn = connect_to_db()
    hlist = db_conn.list_collection_names()

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

        if(len(dates) == 0):
            continue

        for k in dates:
            try:
                for p in jsondata[k]:
                    csv_info = str(k) + "," + str(p["CPU"]) + "," + str(p["RAM"]) + "," + str(p["RDISK"]) + "," + str(p["WDISK"]) + "\n"
                    csv_file = dat_dir + p["name"].replace("/", "-") + "_" + p["pid"] + ".csv"

                    f = open(csv_file, "a")
                    f.write(csv_info)
                    f.close()
            except Exception as error:
                print("No data structure found", error)            

if __name__ == "__main__":
	main()