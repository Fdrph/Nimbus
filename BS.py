#!/usr/bin/python3
import socket
import sys
import argparse

# Redes de Computadores 2018
# Cloud Backup using sockets
# 
# group 8

# Argument Parser for BSname and BSport
parser = argparse.ArgumentParser(description='Backup Server')
parser.add_argument('-b', '--bsport', type=int, default=59000, help='Backup Server port')
parser.add_argument('-n', '--bsname', default='localhost', help='Backup Server name')
parser.add_argument('-p', '--csport', type=int, default=58008, help='Central Server port')
input_args = vars(parser.parse_args())

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ('localhost', input_args['csport'])
# sock.bind(addr)


sock.sendto(b'hello', addr)
# while True:
# 	msg1 = b'RECEIVED: OKAY.'
# 	print ("waiting for data....")
# 	data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
# 	print ("received message:", data)
# 	sock.sendto(msg1, addr)
# 	#print (addr)
