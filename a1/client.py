#!/usr/bin/python3

import sys
import socket


# Create socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind socket to port
server_address = ('localhost', 58000)
print("connecting to: %s port: %d" % server_address)
sock.connect(server_address)



try:
    # Send data
    message = b'This is the message.  It will be repeated.'
    print("sending: {!r}".format(message))
    sock.sendall(message)

    # Look for the response
    amount_received = 0
    amount_expected = len(message)

    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print("received: {!r}".format(data))

finally:
    print('closing socket')
    sock.close()