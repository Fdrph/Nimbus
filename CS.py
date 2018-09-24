#!/usr/bin/python3
import socket
import sys
import argparse

# Redes de Computadores 2018
# Cloud Backup using sockets
# 
# group 8


# Argument Parser for CSname and CSport
parser = argparse.ArgumentParser(description='User Server')
parser.add_argument('-p', '--csport', type=int, default=58008, help='Central Server port')
args = vars(parser.parse_args())

# debug
print(args)

#Create socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind socket to port

local_hostname = socket.gethostname()
server_address = ("localhost", args["csport"])
#server_address = (socket.gethostbyname(local_hostname), args["csport"])
print("starting up on: %s port: %s" % server_address)
sock.bind(server_address)

print('listening...')
# Listen for incoming connections
sock.listen(1)



while True:
    # Accept conection
    connection, client_address = sock.accept()

    print('Accepting conection from: ', client_address)


    while True:
            data = connection.recv(16)
            print('received {!r}'.format(data))
