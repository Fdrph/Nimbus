#!/usr/bin/python3

import sys
import socket


# Create socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind socket to port
server_address = ('localhost', 58000)
print("starting up on: %s port: %s" % server_address)
sock.bind(server_address)

print('listening...')
# Listen for incoming connections
sock.listen(1)


# Wait for a connection
while True:
    # Accept conection
    connection, client_address = sock.accept()

    try:
        print('Accepting conection from: ', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            print('received {!r}'.format(data))
            if data:
                print('sending data back to the client')
                connection.sendall(data)
            else:
                print('no data from', client_address)
                break
            
    finally:
        # Clean up the connection
        connection.close()