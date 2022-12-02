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
	data = json.loads(message)
	event = data["event"]

	print("EVENT: " + str(event))

	if (event == "join-net"):
		print("USER JOINED THE NETWORK")
	elif (event == "disconnect"):
		#remove this user id from the list of peers
		global peerids
		while (peerids.count(data["userid"])):
			peerids.remove(data["userid"])
	elif (event == "get-peers"):
		#add the new peers to the list of peer ids
		global peerids
		peerids = peerids + data["peers"]
	elif (event == "relay-get"):
		pass
	elif (event == "relay-put"):
		pass
	elif (event == "relay-get-response"):
		pass

#a function for handling errors with a websocket connection
def onSocketError(ws, error):
	print("WEBSOCKET ERROR: " + str(error))

#a function for handling a closing socket connection
def onSocketClose(ws, status_code, close_msg):
	print("WEBSOCKET CONNECTION CLOSED: " + str(close_msg))


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
def putData(websocket, key, data, echo=0):
	#store data in local storage first

	#make an object for storing data as a key-value pair
	dataObj = {"key": key, "value": data, "userid": userid, "event": "relay-put", "peers": peerids, "echo": echo, "batonholders": []}

	#send the request to each peer
	for peerid in peerids:
		dataObj["recipient"] = peerid
		websocket.send(json.dumps(dataObj))

#a function for getting data stored on the network
def getData(websocket, key, echo=0):
	#check for data in local storage first

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
	websocket.enableTrace(True)
	ws = connectSocket("ws://localhost:8000/signal")

	#run the websocket connection and listen for events
	ws.run_forever(dispatcher=rel)
	rel.signal(2, rel.abort)
	rel.dispatch()

#execute the main code
main()
