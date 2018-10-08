import socket

UDP_IP = "localhost"
UDP_PORT = 50823
MESSAGE = "Hello World!"

print("UDP target IP: ", UDP_IP)
print("UDP target port: ", UDP_PORT)
print("Message: ", MESSAGE)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))