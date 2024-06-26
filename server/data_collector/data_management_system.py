import config as cfg

def data_filter(data, sys_params):
	try:
		date = data[0:19]
		sysuptime = float(data[19:data.index("||\n")])
		data = data[data.index("||\n")+3:len(data)]
		d = {}
		rdata = []
		segmented_data = data.split("||\n")
		
		for i in range(0, len(segmented_data)-1):
			fcnt = i % 4
			if(fcnt == 0):
				pname = cfg.re.findall("\(.*\)", segmented_data[i])[0]
				segmented_data[i] = segmented_data[i].replace(pname + " ", "")	
				segmented_file = segmented_data[i].split(" ")

				start_time = float(segmented_file[20])
				total_time = float(segmented_file[12]) + float(segmented_file[13])
				
				prseconds = sysuptime - (start_time / sys_params[0])
				result = round(100 * ((total_time / sys_params[0]) / prseconds), 2)
				pid = segmented_file[0]
				d.update({"pid" : segmented_file[0]})
				d.update({"name" : pname})
				d.update({"status" : segmented_file[1]})
				d.update({"CPU" : str(result)})
				d.update({"TOTALTIME" : str(prseconds)})

			elif(fcnt == 1):
				ram_usage = cfg.re.findall("VmRSS:.*", segmented_data[i])
				if ram_usage == []:
					ram_usage = 0
				else:
					ram_usage = ram_usage[0].split("\t")[1].replace(" ", "")
					ram_usage = float(ram_usage[0:len(ram_usage)-2])

				result = round(100 * (ram_usage / sys_params[1]), 2)		

				d.update({"RAM" : str(result)})

			elif(fcnt == 2):
				segmented_file = segmented_data[i].split("\n")	

				d.update({"RDISK" : segmented_file[0][7:len(segmented_file[0])], "WDISK" : segmented_file[1][7:len(segmented_file[1])]})
			
			elif(fcnt == 3):
				sc = []
				pt = []
				of = []

				sc = set(cfg.re.findall("socket:\[.*\]", segmented_data[i]))
				pt = set(cfg.re.findall("/dev/pts/.*", segmented_data[i]))
				of = set(segmented_data[i].split("\n"))

				of = of - sc
				
				of = list(of - pt)

				sc = list(sc)
				pt = list(pt)
				of.remove("")

				d.update({"NSOCKETS" : str(len(sc))})
				d.update({"NTERMS" : str(len(pt))})
				d.update({"NFILES" : str(len(of))})

				rdata.append(d.copy())

		return {date : rdata}
	
	except:
		return None

#password123
def connect_to_db(msclient):
	client = cfg.MongoClient(cfg.MONGO_DIR)
	col = cfg.COLLECTION + msclient.replace(".", "_")
	return client[cfg.DB][col]

def get_initial_setup(q):
	while True:
		if(len(q) > 0):
			data = q.pop(0)
			data = data[1:len(data)-1].split(",")
			return float(data[0]), float(data[1]), float(data[2])/1024

def data_management(q, msclient):
	col = connect_to_db(msclient)
	uptime, hertz, totram = get_initial_setup(q)
	while True:
		if(len(q) > 0):
			data = q.pop(0)
			pr_data = data_filter(data, [hertz, totram])
			
			if pr_data == None:
				pass
			else:
				col.insert_one(pr_data)