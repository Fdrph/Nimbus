import socket

IP = socket.gethostbyname(socket.gethostname())
PORT = 5005

MESSAGE = "Hello World!"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
s.send(MESSAGE.encode())
data = s.recv(1024).decode()
s.close()

print ("received data:", data)