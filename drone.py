import os
import time
import uuid
import json
import asyncio
import websockets
import threading

#global peer ids variable for keeping track of peers
peerids = []

#random user id for the network
userid = str(uuid.uuid1())

#a data cache of outside data not stored locally
cache = {}

#a cache for queues that represent events
event_cache = {}

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
FUNCTIONS DEALING WITH WEBSOCKETS AND EVENTS
'''

#a function to join the websocket network
async def joinNet(ws, attrs):
	#make the request for joining the network
	joinObj = {"userid": userid, "event": "join-net", "attributes": attrs}
	joinObj = json.dumps(joinObj)

	#send the request
	await ws.send(joinObj)

#a function for requesting peers
async def getPeers(ws):
	#make the request for peers
	getPeersObj = {"userid": userid, "event": "get-peers"}
	getPeersObj = json.dumps(getPeersObj)

	#send the request
	await ws.send(getPeersObj)

#a function to disconnect from the network
async def disconnectNet(ws):
	#make the request to disconnect from the network
	disconnectObj = {"userid": userid, "event": "disconnect", "peerids": peerids}
	disconnectObj = json.dumps(disconnectObj)

	#send the request
	await ws.send(disconnectObj)

#a function for storing data on the network
async def putData(ws, key, data, echo=1):
	#store data in local storage first
	writeData(key, data)

	#make an object for storing data as a key-value pair
	dataObj = {"key": key, "value": data, "userid": userid, "event": "relay-put", "peers": peerids, "echo": echo, "batonholders": []}

	#send the request to each peer
	for peerid in peerids:
		dataObj["recipient"] = peerid
		await ws.send(json.dumps(dataObj))

#a function for requesting data stored on the network
async def getData(ws, event_cache, key, echo=1):
	#check for data in local storage first
	localdata = readData(key)
	if (localdata != None):
		return localdata
	else:
		#make an object for requesting data
		dataObj = {"key": key, "userid": userid, "event": "relay-get", "echo": echo, "batonholders": []}

		#make a new queue for this data request
		event_cache[key] = asyncio.Queue()

		print(peerids)

		#send the request to each peer
		for peerid in peerids:
			dataObj["recipient"] = peerid
			await ws.send(json.dumps(dataObj))

		#wait for data to be returned from the network, otherwise return none
		try:
			result = await asyncio.wait_for(event_cache[key].get(), timeout=1.0)
			return cache[key]
		except TimeoutError:
			return None

#a function for torrenting a file on the network
async def torrentFile(websocket, filepath):
	#if this filepath does not exist, dont torrent the file
	if (not os.path.exists(filepath)):
		return False

	#open the file provided from the local machine
	file = open(filepath)

	#get the name of this file to use as a reference on the network
	filename = os.path.basename(filepath)

	#get the contents of this file
	filecontent = file.readlines()

	#a list of fragment keys
	fragments = []

	#torrent each line in this file
	for index, line in enumerate(filecontent):
		#store this fragment of data on the network
		fragment = filename + "_" + str(index)
		await putData(websocket, fragment, line)

		#add this fragment id to the fragments list
		fragments.append(fragment)

	print("FILE FRAGMENTS:")
	print(fragments)

	#store a ledger for this file
	ledger_key = filename + "_ledger"
	await putData(websocket, ledger_key, fragments)

	#torrenting was successful
	return True

#a function for downloading a torrented file
async def downloadTorrent(websocket, filename):
	#use the global event cache
	global event_cache

	#get the ledger for this file
	ledger_key = filename + "_ledger"
	ledger = await getData(websocket, event_cache, ledger_key)

	#if this file ledger does not exist, then return none
	if (not ledger):
		return False

	#a list of the fragments/lines of the file
	fragments = []

	#get the fragments from the network
	for fragment in ledger:
		frag = await getData(websocket, event_cache, fragment)
		fragments.append(frag)

	#get a timestamp for the download
	timestamp = str(round(time.time()))

	#write fragments to the new file locally
	download_file = open("./"+timestamp+"-"+filename, "w")
	for fragment in fragments:
		download_file.write(fragment)
	download_file.close()

'''
THE CONSUMER AND PRODUCERS OF WEBSOCKET MESSAGES
'''

#loops through the messages recieved by the websocket
async def wsConsume(websocket, event_cache):
	#loop through the recieved messages
	async for message in websocket:
		global peerids

		#get the data and event type of this message
		data = json.loads(message)
		event = data["event"]

		print("EVENT: " + event)

		#execute code based on the event type
		if (event == "join-net"):
			#add this peer if the amount of connected peers are less than 10
			if (len(peerids) < 10):
				peerids.append(data["peerid"])

			await event_cache["data-ready"].put("data-ready")

		elif (event == "disconnect"):
			#remove this user id from the list of peers
			while (peerids.count(data["userid"])):
				peerids.remove(data["userid"])

		elif (event == "get-peers"):
			#add the new peers to the list of peer ids
			peerids = peerids + data["peers"]

			if (len(peerids)):
				await event_cache["data-ready"].put("data-ready")

		elif (event == "relay-get"):
			#check local data first
			value = readData(data["key"])

			#if the data is found or if the baton holder limit is reached, send the data back to the requester, otherwise pass it on
			if (value != None or len(data["batonholders"]) == data["echo"]):
				#make the relay get response
				valueObj = {"userid": userid, "event": "relay-get-response", "key": data["key"], "value": value, "recipient": data["userid"], "batonholders": data["batonholders"]}
				valueObj = json.dumps(valueObj)

				#send this data back to the original user/requester on the network
				await websocket.send(valueObj)
			else:
				#add our user id to the batonholders
				data["batonholders"].append(userid)

				#make a request for data to relay to other peers on the network
				dataObj = {"key": data["key"], "userid": data["userid"], "event": "relay-get", "echo": data["echo"], "batonholders": data["batonholders"]}

				#send this relay request to other peers on the network
				for peerid in peerids:
					dataObj["recipient"] = peerid
					await websocket.send(json.dumps(dataObj))

		elif (event == "relay-put"):
			#write this piece of data to the local storage
			writeData(data["key"], data["value"])

			#add the user id to the baton holders
			data["batonholders"].append(userid)

			#if the echo limit has not been reached, then echo this message to other peers on the network
			if (len(data["batonholders"]) < data["echo"]):
				for peerid in peerids:
					await websocket.send(json.dumps(data))

		elif (event == "relay-get-response"):
			#store this value in the cache dictionary
			cache[data["key"]] = data["value"]

			#add this event to the queue
			await event_cache[data["key"]].put("relay-get-response")

#do all of the interaction with the network here
async def wsProduce(websocket, event_cache):
	#join the network
	await joinNet(websocket, {"name": "example"})

	#get peers on the network
	await getPeers(websocket)

	#wait for a result/list of peers before proceeding
	result = await event_cache["data-ready"].get()
	example_result = await getData(websocket, event_cache, "example")

	print("GOT DATA: " + str(example_result))

	await torrentFile(websocket, "./example.txt")
	await downloadTorrent(websocket, "example.txt")

'''
THE MAIN EVENT LOOP AND PROGRAM STARTING POINT
'''

#the main function to run
async def main(wss):
	#use the global event cache variable
	global event_cache

	#make a websocket connection to the server
	websocket = await websockets.connect(wss)

	#make a queue/event for when data interaction is ready
	event_cache["data-ready"] = asyncio.Queue()

	#execute the websocket consumer and producer routines
	await asyncio.gather(
		wsConsume(websocket, event_cache),
		wsProduce(websocket, event_cache)
	)

	'''
	#close the connection once done
	print("CLOSING CONNECTION")
	await disconnectNet(websocket)
	await websocket.close()
	'''

#run the main function
asyncio.run(main("ws://localhost:8000/signal"))
