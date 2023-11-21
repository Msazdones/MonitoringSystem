import re

def filter_data(data):
	rdata = dict() #{"pid" : 0, "name" : "", "status" : "", "CPU" : 0.0, "RAM" : 0.0, "RDISK" : 0, "WDSIK" : 0}

	segmented_data = data.split("\n||\n")
	
	for i in range(0, len(segmented_data)-1):
		fcnt = i % 3
		if(fcnt == 0):
			rdata.update({"pid" : segmented_data[i][0]})
			#rdata.update({"name" : segmented_data[i][0]})
			#print(re.match("\(.*\)", segmented_data[i]))
		elif(fcnt == 1):
			print("aaaa2")

		elif(fcnt == 2):
			print("aaaa3")

	return 0

def data_management(q):
	while True:
		if(len(q) > 0):
			data = q.pop(0)
			pr_data = filter_data(data)
			
