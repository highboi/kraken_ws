import asyncio
import websockets
import json
import random

#a global dictionary of clients on the network
signalClients = {}

#function for processing requests to the server
async def process(websocket):

	#get the remote ip address of this peer on the local network
	peerinfo = websocket.remote_address

	print(peerinfo)

	#loop through each message sent to the websocket
	async for message in websocket:
		#process each request as json
		data = json.loads(message)
		event = data["event"]

		print("EVENT: " + str(event))

		#respond to different types of events
		if (event == "join-net"):
			#add this client to the global dictionary
			signalClients[data["userid"]] = {"userid": data["userid"], "socket": websocket, "attributes": data["attributes"]}

			#make a message to the other clients about a new peer
			peerJoinObj = {"event": "join-net", "peerid": data["userid"], "peerattributes": data["attributes"]}
			peerJoinObj = json.dumps(peerJoinObj)

			#send the new peer to each client on the network
			for peerid in signalClients:
				if (peerid != data["userid"]):
					await signalClients[peerid]["socket"].send(peerJoinObj)
		elif (event == "disconnect"):
			#remove the entry for this user id from the signal clients
			signalClients.pop(data["userid"])

			#make the packet to send to all peers
			disconnectObj = {"userid": data["userid"], "event": "disconnect"}
			disconnectObj = json.dumps(disconnectObj)

			#send this disconnect to all of the peers this node is connected to
			for peerid in data["peerids"]:
				await signalClients[peerid]["socket"].send(disconnectObj)
		elif (event == "get-peers"):
			#get a random number of peers
			peerids = list(signalClients.keys())
			random.shuffle(peerids)
			peerids = peerids[:6]

			#remove this peers user id from the array if it happens to be in there
			if (data["userid"] in peerids):
				peerids.remove(data["userid"])

			#make the object to send to the client
			peersObj = {"event": "get-peers", "peers": peerids, "userid": data["userid"]}
			peersObj = json.dumps(peersObj)

			#send the client the peers to connect to
			await signalClients[data["userid"]]["socket"].send(peersObj)
		elif (event == "relay-get"):
			#relay this get request to the proper recipient
			await signalClients[data["recipient"]]["socket"].send(json.dumps(data))
		elif (event == "relay-put"):
			#relay this data writing to the proper recipient
			await signalClients[data["recipient"]]["socket"].send(json.dumps(data))
		elif (event == "relay-get-response"):
			#send data on the network back to the proper recipient
			await signalClients[data["recipient"]]["socket"].send(json.dumps(data))


#the main point of execution
async def main():
	print("BOOTING WEBSOCKET SERVER...")

	#run the server indefinitely
	async with websockets.serve(process, "localhost", 8000):
		await asyncio.Future()

#run the server
asyncio.run(main())
