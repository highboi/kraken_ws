#import necessary modules
from sanic import Request, Websocket, Sanic
from pprint import pprint
import random
import json

#make the mothership app
app = Sanic("mothership")

#a dictionary to store all of the active connections
signalClients = {}

#a function for handling signals to the websocket server
async def signal(request: Request, ws: Websocket):
	print()
	print(request)
	print(ws)

	#look at the messages being sent
	async for msg in ws:
		#get the data and event type of this message
		data = json.loads(msg)
		event = data["event"]

		print("EVENT: " + event)

		#perform different tasks based on the event of the message
		if (event == "join-net"): #add a client to the network
			#add this user to the signal clients
			signalClients[data["userid"]] = {"userid": data["userid"], "socket": ws, "attributes": data["attributes"]}

			#make a message to the other clients about a new peer
			peerJoinObj = {"event": "join-net", "peerid": data["userid"], "peerattributes": data["attributes"]}
			peerJoinObj = json.dumps(peerJoinObj)

			#send the new peer to each client on the network
			for peerid in signalClients:
				if (peerid != data["userid"]):
					await signalClients[peerid]["socket"].send(peerJoinObj)
		elif (event == "disconnect"): #remove a client from the network
			#remove the entry for this user id from the signal clients
			signalClients.pop(data["userid"])

			print(data)

			#make the packet to send to all peers
			disconnectObj = {"userid": data["userid"], "event": "disconnect"}
			disconnectObj = json.dumps(disconnectObj)

			#send this disconnect to all of the peers this node is connected to
			for peerid in data["peerids"]:
				await signalClients[peerid]["socket"].send(disconnectObj)
		elif (event == "get-peers"): #deliver a random number of peers
			#get a random number of peers
			peerids = list(signalClients.keys())
			random.shuffle(peerids)
			peerids = peerids[:6]

			print(peerids)

			#remove this peers user id from the array if it happens to be in there
			if (data["userid"] in peerids):
				peerids.remove(data["userid"])

			print(peerids)

			#make the object to send to the client
			peersObj = {"event": "get-peers", "peers": peerids, "userid": data["userid"]}
			peersObj = json.dumps(peersObj)

			#send the client the peers to connect to
			await signalClients[data["userid"]]["socket"].send(peersObj)
		elif (event == "relay-get"): #relay a request for data on the network
			#send this request to the recipient on the network on the network
			await signalClients[data["recipient"]]["socket"].send(json.dumps(data))
		elif (event == "relay-put"):
			#send this writing of data to the recipient on the network
			await signalClients[data["recipient"]]["socket"].send(json.dumps(data))
		elif (event == "relay-get-response"):
			#send this get response to the recipient
			await signalClients[data["recipient"]]["socket"].send(json.dumps(data))
		elif (event == "sdp-offer"):
			#construct the sdp offer object
			sdpOffer = {"offer": data["offer"], "event": "sdp-offer", "userid": data["userid"]}
			sdpOffer = json.dumps(sdpOffer)

			#send the sdp offer to each peer
			for peerid in data["peers"]:
				await signalClients[peerid]["socket"].send(sdpOffer)
		elif (event == "sdp-answer"):
			#construct the sdp answer object
			sdpAnswer = {"answer": data["answer"], "event": "sdp-answer", "userid": data["userid"]}
			sdpAnswer = json.dumps(sdpAnswer)

			#send the sdp answer to the recipient
			await signalClients[data["recipient"]]["socket"].send(sdpAnswer)
		elif (event == "answer-pong"):
			#construct the answer pong object
			answerPong = {"event": "answer-pong", "userid": data["userid"]}
			answerPong = json.dumps(answerPong)

			#send the answer pong to the recipient
			await signalClients[data["recipient"]]["socket"].send(answerPong)
		elif (event == "ice-exchange"):
			#construct the ice candidate object
			iceCandidate = {"event": "ice-exchange", "candidate": data["candidate"], "userid": data["userid"]}
			iceCandidate = json.dumps(iceCandidate)

			#send this ice candidate to all relevant peers on the network
			for peerid in data["peers"]:
				await signalClients[peerid]["socket"].send(iceCandidate)
		elif (event == "webrtc-failed"):
			#construct the failed webrtc object
			failedObj = {"event": "webrtc-failed", "userid": data["userid"]}
			failedObj = json.dumps(failedObj)

			#send the webrtc failure to the recipient
			await signalClients[data["recipient"]]["socket"].send(failedObj)

		print()
	print()

#add a route to the websocket server
app.add_websocket_route(signal, "/signal")

#run the application
app.run()
