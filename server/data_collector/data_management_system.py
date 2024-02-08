import config as cfg

def filter_data(data, sys_params):
	date = data[0:19]
	sysuptime = float(data[19:data.index("||\n")])
	data = data[data.index("||\n")+3:len(data)]
	d = {}
	rdata = []
	segmented_data = data.split("||\n")
	for i in range(0, len(segmented_data)-1):
		fcnt = i % 3
		if(fcnt == 0):
			pname = cfg.re.findall("\(.*\)", segmented_data[i])[0]
			segmented_data[i] = segmented_data[i].replace(pname + " ", "")	
			segmented_file = segmented_data[i].split(" ")

			start_time = float(segmented_file[20])
			total_time = float(segmented_file[12]) + float(segmented_file[13])
			
			prseconds = sysuptime - (start_time / sysuptime)
			result = round(100 * ((total_time / sys_params[0]) / prseconds), 2)
			
			d.update({"pid" : segmented_file[0]})
			d.update({"name" : pname})
			d.update({"status" : segmented_file[2]})
			d.update({"CPU" : str(result)})
			d.update({"TOTALTIME" : str(prseconds)})

			#print(d)

		elif(fcnt == 1):
			segmented_file = segmented_data[i].split(" ")
			result = round(100 * (int(segmented_file[0]) / sys_params[1]), 2)
			
			d.update({"RAM" : str(result)})

		elif(fcnt == 2):
			segmented_file = segmented_data[i].split("\n")	

			d.update({"RDISK" : segmented_file[0][7:len(segmented_file[0])], "WDISK" : segmented_file[1][7:len(segmented_file[1])]})
			rdata.append(d.copy())
	
	return {date : rdata}

#password123
def connect_to_db(msclient):
	client = cfg.MongoClient(cfg.MONGO_DIR)
	col = cfg.COLLECTION + msclient.replace(".", "_")
	return client[cfg.DB][col]

def initial_setup(q):
	while True:
		if(len(q) > 0):
			data = q.pop(0)
			data = data[1:len(data)-1].split(",")
			return float(data[0]), float(data[1]), float(data[2])

def data_management(q, msclient):
	col = connect_to_db(msclient)
	uptime, hertz, totmenpages = initial_setup(q)
	while True:
		if(len(q) > 0):
			data = q.pop(0)
			pr_data = filter_data(data, [hertz, totmenpages])
			col.insert_one(pr_data)