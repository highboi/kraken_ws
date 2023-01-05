import asyncio
import socket
import json
import threading

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

#the main function to get into contact with the signalling server to get peer ip/port pairs
def main(host, port):
	#use the global peers variable for managing peers on the network
	global peers

	#make a new socket
	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#connect to the host/port pair defined in the function parameters
	soc.connect((host, port))

	#make the request for peers from the server
	getPeersObj = {"event": "get-peers"}
	getPeersObj = json.dumps(getPeersObj)

	#send the request for peers
	soc.sendall(getPeersObj)

	#the loop for recieving data from the signalling server
	while True:
		#wait for data to be recieved on this connection
		data = soc.recv(4096)

		#parse the data as json
		data = json.loads(data)
		event = data["event"]

		#check for a message about recieving a list of peers from the server
		if (event == "get-peers"):
			#get the peers
			peerips = data["peerips"]

			#add the peers to the global variable for peers on the network
			for (peer in peerips):
				peers.append([peer["ip"], peer["port"]])

			#break the while loop once peers are recieved from the signalling server
			print("recieved peers, breaking the loop for the signalling server")
			break

	#disconnect the socket from the signalling server
	soc.close()

#a function for managing the recieving and sending of messages on the network
def managePeer(sock):
	#recieve messages for this socket until there is no data
	while True:
		#recieve and parse data
		data = sock.recv(4096)
		if not data:
			break
		else:
			data = json.loads(data)
			event = data["event"]

		#process data here
		if (event == "disconnect"):
			peers.remove()
		elif (event == "relay-get"):
			pass
		elif (event == "relay-put"):
			pass
		elif (event == "relay-get-response"):
			pass

#a function to connect to peers on the network for interaction
def connectPeers():
	#access the global list of peers
	global peers

	#an array for peer sockets to manage
	peer_sockets = []

	#make socket connections for all peers
	for (peer in peers):
		#make a socket and connect to this peer
		soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		soc.connect((peer[0], peer[1]))

		#add this active socket to the peer sockets
		peer_sockets.append(soc)

	#execute routines for managing produce/consume cycle of sockets

#get peers from the signalling server
main("beacon.wrt", 8000)
