import socket
import json

#an array to store ip/port tuples for communication
peers = []

#a cache for data not stored locally
cache = {}

'''
FUNCTIONS FOR HANDLING STORAGE OF DATA LOCALLY
'''

#function for initializing a simple database
def initData():
	#create a database txt file if it does not exist
	if (not os.path.exists("./database.txt")):
		#create the new file
		file = open("database.txt", "x")
		file.close()

		#write data to the new file
		file = open("database.txt", "w")
		file.write("{}")
		file.close()

#function for reading data from the simple db
def readData(key):
	#open the file and read the contents
	file = open("./database.txt", "r")
	data = file.read()
	data = json.loads(data)
	file.close()

	#check if the data exists or not
	if (key in data):
		return data[key]
	else:
		return None

#function for writing data to the simple db
def writeData(key, value):
	#read current data in the file and alter it
	file = open("./database.txt", "r")
	data = file.read()
	data = json.loads(data)
	data[key] = value
	file.close()

	#write the new data to the file
	file = open("database.txt", "w")
	file.write(json.dumps(data))
	file.close()

#initialize the simple database
initData()

'''
CODE FOR SOCKET SIGNALLING AND IP/PORT EXCHANGE
'''

#a function to process recieved data

#a function to send responses to a socket peer/server

#start interaction with a peer or host
def socketStart(host, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	sock.connect((host, port))

	#make the request to join the network
	joinObj = {"userid": userid, "event": "join-net", "attributes": attrs}
	joinObj = json.dumps(joinObj)

	#send the request to join the network and be listed among the peers
	sock.send(bytes(joinObj, "utf-8"))
