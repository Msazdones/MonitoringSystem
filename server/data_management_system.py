import re
from pymongo import MongoClient

def filter_data(data):
	rdata = dict() #{"pid" : 0, "name" : "", "status" : "", "CPU" : 0.0, "RAM" : 0.0, "RDISK" : 0, "WDSIK" : 0}

	segmented_data = data.split("\n||\n")
	cnt1 =0
	cnt2 =0
	cnt3 =0
	
	for i in range(0, len(segmented_data)-1):
		fcnt = i % 3
		if(fcnt == 0):
			pass
			#cnt1 = cnt1+1
			#segmented_file = data.split(" ")
			#print(segmented_file[0], segmented_file[1])
			#rdata.update({"pid" : segmented_data[i][0]})
			#rdata.update({"name" : segmented_data[i][segmented_data[i].find("(")+1:segmented_data[i].find(")")]})
		elif(fcnt == 1):
			pass
			#cnt2 = cnt2+1
			#print("aaaa2")
			#pass
		elif(fcnt == 2):
			pass
			#cnt3 = cnt3+1
			#print("aaaa3")
			#pass
	#print(cnt1, cnt2, cnt3)
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
			return int(data[0]), int(data[1])

def data_management(q):
	#db = connect_to_db()
	#collection = db["user_1_items"]
	totmenpages, hertz = initial_setup(q)
	print(totmenpages, hertz)
	while True:
		if(len(q) > 0):
			print(len(q), q)
			data = q.pop(0)
			print(data)
			pr_data = filter_data(data)
			
