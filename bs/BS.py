#!/usr/bin/python3
import socket
import sys
import argparse
import signal
import selectors

# Redes de Computadores 2018
# Cloud Backup using sockets
# 
# group 8

# Argument Parser for BSname and BSport
parser = argparse.ArgumentParser(description='Backup Server')
parser.add_argument('-b', '--bsport', type=int, default=59000, help='Backup Server port')
parser.add_argument('-n', '--csname', default='localhost', help='Central Server name')
parser.add_argument('-p', '--csport', type=int, default=58008, help='Central Server port')
cmd_line_args = vars(parser.parse_args())

hostname =  socket.gethostbyname(socket.gethostname())
sel = selectors.DefaultSelector()

# TCP session with user
def tcp_session(sock, udp_sock):
    data, addr = sock.recvfrom(1024)
    if data:
        print('received ', repr(data))
        sock.sendall(b'AUR OK\n')
    else:
        print('closing ', sock.getsockname())
        sel.unregister(sock)
        sock.close()

def tcp_accept(sock):
    connection, client_address = sock.accept()
    print('Accepting user connection from: ', client_address)
    connection.setblocking(False)
    sel.register(connection, selectors.EVENT_READ, tcp_session)

def udp_cs(sock):
	print('')






def register_with_cs():
	udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	cs_addr = (cmd_line_args['csname'], cmd_line_args['csport'])

	rgr = "REG " + hostname + ' ' + str(cmd_line_args['bsport']) + '\n'
	try:
		udp_sock.sendto(rgr.encode('UTF-8'), cs_addr)
	except socket.error:
		udp_sock.close()
		return False

	status = udp_sock.recv(1024)
	# print(status)
	if status.decode('UTF-8').split()[1] != 'OK':
		udp_sock.close()
		return False
	udp_sock.close()
	return True

if not register_with_cs():
	print("Couldn't register with central server!")
	exit()
else:
	print("Registered sucessfully with central server!")


# UDP
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cs_addr = (cmd_line_args['csname'], cmd_line_args['csport'])
udp_sock.setblocking(False)
sel.register(udp_sock, selectors.EVENT_READ, udp_cs)

# TCP
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_address = (hostname, cmd_line_args["csport"])
server_address = ('localhost', cmd_line_args['bsport'])
tcp_sock.bind(server_address)
print('listening for users...')
tcp_sock.listen()
tcp_sock.setblocking(False)
sel.register(tcp_sock, selectors.EVENT_READ, tcp_accept)


def sig_handler(sig, frame):
    sel.unregister(udp_sock)
    udp_sock.setblocking(True)

    snd = 'UNR '+hostname+' '+str(cmd_line_args['bsport'])+'\n'
    udp_sock.sendto(snd.encode('UTF-8'), (cmd_line_args['csname'], cmd_line_args['csport']) )
    msg = udp_sock.recv(1024).decode('UTF-8').rstrip('\n')
    # print(msg)
    if msg != 'UAR OK':
        print("Couldn't unregister with central server!")

    udp_sock.close()
    sel.unregister(tcp_sock)
    tcp_sock.close()
    print("\nExiting Backup server...")
    exit()
signal.signal(signal.SIGINT, sig_handler)


while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        if callback == tcp_session:
            callback(key.fileobj, udp_sock)
        else:
            callback(key.fileobj)
