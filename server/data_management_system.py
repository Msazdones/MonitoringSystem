import re
from pymongo import MongoClient

def filter_data(data, sys_params):
	rdata = dict() #{"pid" : 0, "name" : "", "status" : "", "CPU" : 0.0, "RAM" : 0.0, "RDISK" : 0, "WDSIK" : 0}

	segmented_data = data.split("||")
	for i in range(0, len(segmented_data)-1):
		start = segmented_data[i].find("|")
		print(segmented_data[i][1:start])
		match segmented_data[i][1:start]:
			case "stat":
				segmented_file = segmented_data[i][start+2:len(segmented_data[i])].split(" ")

				start_time = float(segmented_file[21])
				total_time = float(segmented_file[13]) + float(segmented_file[14])
				prseconds = sys_params[0] - (start_time / sys_params[1])
				result = 100 * ((total_time / sys_params[1]) / prseconds)
				print(result)
			case "statm":
				segmented_file = segmented_data[i][start+2:len(segmented_data[i])].split(" ")
				print(segmented_file)
			case "io":
				segmented_file = segmented_data[i][start+2:len(segmented_data[i])].split("\n")
				print(segmented_file)
				#print("io")
			case _:
				print("Error")
	return 0

def connect_to_db():
	direction = "mongodb+srv://user:pass@cluster.mongodb.net/myFirstDatabase"
	client = MongoClient(direction)
	return client['monitoring_sys']

def initial_setup(q):
	while True:
		if(len(q) > 0):
			data = q.pop(0)
			data = data[1:len(data)-1].split(",")
			print(data)
			return float(data[0]), float(data[1]), float(data[2])

def data_management(q):
	#db = connect_to_db()
	#collection = db["user_1_items"]
	uptime, hertz, totmenpages = initial_setup(q)
	while True:
		if(len(q) > 0):
			data = q.pop(0)
			pr_data = filter_data(data, [uptime, hertz, totmenpages])
			
