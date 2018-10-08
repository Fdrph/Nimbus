import socket

IP = socket.gethostbyname(socket.gethostname())
PORT = 5005

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, PORT))
s.listen(1)

conn, addr = s.accept()
print ('Connection address:', addr)

data = conn.recv(20).decode()
print ("received data:", data)
conn.send(data.encode())
conn.close()
