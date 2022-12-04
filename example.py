import threading

def hello():
	print("hello")

t = threading.Timer(3.0, hello)
t.start()

print("hi")
