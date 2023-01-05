import socket
import sys

host, port = "localhost", 8000
data = " ".join(sys.argv[1:])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect((host, port))

print(sock.getsockname())
print(sock.getpeername())

sock.sendall(bytes(data + "\n", "utf-8"))

while True:
	recieved = str(sock.recv(4096), "utf-8")
	print(recieved)

	sock.send(b"example")
