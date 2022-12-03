#import the necessary modules
#import eel
#import random
#import asyncio
import json
import uuid
import websocket
import rel
import time
import _thread
import os
import threading


'''
#choose a random port to make the local server
eelport = random.randrange(1000, 10000, 1)
print("RUNNING APPLICATION ON PORT: " + str(eelport))

#initialize the application and start it using the portal
eel.init("web")
eel.start("portal.html", port=eelport, size=(1200, 1000))
'''

'''
GLOBAL VARIABLES
'''

#a global variable for the websocket
ws = None

#a global variable to store peers to communicate with
peerids = []

#generate a unique user id
userid = str(uuid.uuid1())

#a global object to store recieved data from peers
datarecv = {}

#a global variable for handling events related to the recieving of data
dataevent = threading.Event()

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
	file = open("database.txt", "r")
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
	file = open("database.txt", "r")
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
FUNCTIONS FOR HANDLING WEBSOCKET EVENTS
'''

#a function for handling a newly opened websocket connection
def onSocketOpen(ws):
	print("CONNECTED TO WEBSOCKET SERVER")

	#join the network on the relay server
	joinNet(ws, {"name": "examplepeer"})

	#request peers to connect to on the network
	getPeers(ws)

#a function for handling messages on the websocket
def onSocketMessage(websocket, message):
	global peerids

	data = json.loads(message)
	event = data["event"]

	print("EVENT: " + str(event))

	if (event == "join-net"):
		print("USER JOINED THE NETWORK")

		#add this peer
		peerids.append(data["peerid"])

		#request data on the network
		getData(ws, "example")
	elif (event == "disconnect"):
		#remove this user id from the list of peers
		while (peerids.count(data["userid"])):
			peerids.remove(data["userid"])
	elif (event == "get-peers"):
		#add the new peers to the list of peer ids
		peerids = peerids + data["peers"]
	elif (event == "relay-get"):
		#check local data first
		value = readData(data["key"])

		#if the data is found or if the baton holder limit is reached, send the data back to the requester, otherwise pass it on
		if (value != None or len(data["batonholders"]) == data["echo"]):
			#make the relay get response
			valueObj = {"userid": userid, "event": "relay-get-response", "key": data["key"], "value": value, "recipient": data["userid"], "batonholders": data["batonholders"]}
			valueObj = json.dumps(valueObj)

			#send this data back to the original user/requester on the network
			websocket.send(valueObj)
		else:
			#add our user id to the batonholders
			data["batonholders"].append(userid)

			#make a request for data to relay to other peers on the network
			dataObj = {"key": data["key"], "userid": data["userid"], "event": "relay-get", "echo": data["echo"], "batonholders": data["batonholders"]}

			#send this relay request to other peers on the network
			for peerid in peerids:
				dataObj["recipient"] = peerid
				websocket.send(json.dumps(dataObj))
	elif (event == "relay-put"):
		#write this piece of data to the local storage
		writeData(data["key"], data["value"])

		#add the user id to the baton holders
		data["batonholders"].append(userid)

		#if the echo limit has not been reached, then echo this message to other peers on the network
		if (len(data["batonholders"]) < data["echo"]):
			for peerid in peerids:
				websocket.send(json.dumps(data))

	elif (event == "relay-get-response"):
		#store the recieved data in local storage and fire an event for getting the data
		print("DATA RESPONSE: " + str(data["key"]) + " " + str(data["value"]))

#a function for handling errors with a websocket connection
def onSocketError(ws, error):
	print("WEBSOCKET ERROR: " + str(error))

#a function for handling a closing socket connection
def onSocketClose(ws, status_code, close_msg):
	print("WEBSOCKET CONNECTION CLOSED: " + str(close_msg))
	print(status_code)


'''
FUNCTIONS FOR SENDING MESSAGES TO THE WEBSOCKET SERVER
'''

#a function for connecting to a websocket server
def connectSocket(uri):
	#make a websocket connection with event handlers
	socket = websocket.WebSocketApp(uri,
				on_open=onSocketOpen,
				on_message=onSocketMessage,
				on_error=onSocketError,
				on_close=onSocketClose)

	return socket

#a function to join the websocket network
def joinNet(websocket, attrs):
	#make the request for joining the network
	joinObj = {"userid": userid, "event": "join-net", "attributes": attrs}
	joinObj = json.dumps(joinObj)

	#send the request
	websocket.send(joinObj)

#a function for requesting peers
def getPeers(websocket):
	#make the request for peers
	getPeersObj = {"userid": userid, "event": "get-peers"}
	getPeersObj = json.dumps(getPeersObj)

	#send the request
	websocket.send(getPeersObj)

#a function to disconnect from the network
def disconnectNet(websocket):
	#make the request to disconnect from the network
	disconnectObj = {"userid": userid, "event": "disconnect", "peerids": peerids}
	disconnectObj = json.dumps(disconnectObj)

	#send the request
	websocket.send(disconnectObj)

#a function for storing data on the network
def putData(websocket, key, data, echo=1):
	#store data in local storage first
	writeData(key, data)

	#make an object for storing data as a key-value pair
	dataObj = {"key": key, "value": data, "userid": userid, "event": "relay-put", "peers": peerids, "echo": echo, "batonholders": []}

	#send the request to each peer
	for peerid in peerids:
		dataObj["recipient"] = peerid
		websocket.send(json.dumps(dataObj))

#a function for getting data stored on the network
def getData(websocket, key, echo=1):
	#check for data in local storage first
	localdata = readData(key)
	if (localdata != None):
		print(localdata)
		return localdata

	#make an object for requesting data
	dataObj = {"key": key, "userid": userid, "event": "relay-get", "echo": echo, "batonholders": []}

	#send the request to each peer
	for peerid in peerids:
		dataObj["recipient"] = peerid
		websocket.send(json.dumps(dataObj))

#the main function to execute code
def main():
	#make the websocket connection
	global ws
	websocket.enableTrace(False)
	ws = connectSocket("ws://localhost:8000/signal")

	#run the websocket connection and listen for events
	ws.run_forever(dispatcher=rel)
	rel.signal(2, rel.abort)
	rel.dispatch()

#execute the main code
main()
