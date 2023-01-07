import socket
import threading

def handle_client(client_sock):
	while True:
		data = client_sock.recv(4096)

		if not data:
			break

		client_sock.sendall(data.upper())

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(("", 8000))

sock.listen()

print("STARTING SOCKET SERVER...")

while True:
	client_sock, client_addr = sock.accept()
	print("New client connected:", client_addr)

	print(client_sock)

	client_thread = threading.Thread(target=handle_client, args=(client_sock,))
	client_thread.start()

sock.close()
