#!/usr/bin/python3
import socket
import sys
import os
import argparse
import time
import signal
import selectors

# Redes de Computadores 2018
# Cloud Backup using sockets
# 
# group 8

# Argument Parser for CSname and CSport
parser = argparse.ArgumentParser(description='User Server')
parser.add_argument('-p', '--csport', type=int, default=58008, help='Central Server port')
cmd_line_args = vars(parser.parse_args())


sel = selectors.DefaultSelector()
registered_BS = [] # registered backup servers online
logged_in_users = set()
last_login = ()

# deals with an AUT request
# checks users file, responds
def aut(args, user_socket):
    # print(args)
    # message to send back
    response = b'AUR '
    username = args[0]
    password = args[1]
    
    with open("user_list.txt", 'a+') as f:
        f.seek(0)
        users = [value.split() for value in f.readlines()]
        f.read()
        nouser = True
        for value in users:
            if value == args:
                # user exists and password is correct
                response += b' OK\n'
                nouser = False
                print("User: " + username)
                # logged_in_users.add((username,password))
                global last_login
                last_login = (username, password)
                break
            elif value[0] == username:
                # user exists password is wrong
                response += b' NOK\n'
                nouser = False
                break
        
        if nouser:
            #create user in file and return AUR NEW
            response += b' NEW\n'
            f.write(username+' '+password+'\n')
            os.mkdir(os.path.realpath('')+'/user_'+username)
            print("New user: " + username)
            # logged_in_users.add((username,password))
            global last_login
            last_login = (username, password)

        
    # print(users)
    # print(response)
    
    user_socket.sendall(response)

# deals with a delete user request
def dlu(args, user_socket):
    print('DLU')
    print(last_login)
    user_socket.sendall(b'DLR OK\n')

# get tcp message until \n is found
def get_msg(sock):
    msg = b''
    while True:
        try:
            slic = sock.recv(1024)
            # print(slic)
            msg += slic
            if msg.find(b'\n') != -1:
                break
        except socket.error:
            continue
    return msg.decode('utf-8').rstrip('\n')

# TCP session with user
def tcp_session(sock, udp_sock):
    sel.unregister(sock)
    sock.setblocking(True) 
    message = get_msg(sock)    

    
    actions = { 
    'AUT':aut,
    'DLU':dlu
    }
    args = message.split()
    callable = actions.get(args[0]) # AUT user pass
    callable(args[1:], sock) # aut( [user,pass] )
 

    print('closing ', sock.getsockname())

    sock.close()

def tcp_accept(sock):
    connection, client_address = sock.accept()
    print('Accepting user connection from: ', client_address)
    connection.setblocking(False)
    sel.register(connection, selectors.EVENT_READ, tcp_session)


# Handles BS registration and unregistration
def udp_rgr(udp_sock):
    msg, addr = udp_sock.recvfrom(1024)
    msg = msg.decode('utf-8').rstrip('\n').split()
    if len(msg) < 3: return
    if msg[0] == 'REG':
        if msg[1:] not in registered_BS:
            registered_BS.append([msg[1],msg[2]])
            udp_sock.sendto(b'RGR OK\n', addr)
            print('+BS: '+msg[1]+' '+msg[2])
        else:
            udp_sock.sendto(b'RGR NOK\n', addr)
    elif msg[0] == 'UNR':
        if msg[1:] in registered_BS:
            registered_BS.remove(msg[1:])
            # print(registered_BS)
            print('-BS: '+msg[1]+' '+msg[2])
            udp_sock.sendto(b'UAR OK\n', addr)
        else:
            udp_sock.sendto(b'UAR NOK\n', addr)


    # else:
    #     udp_sock.sendto(b'RGR ERR\n', addr)




print("Server starting up on: %s port: %s" % ('localhost', cmd_line_args['csport']))
# UDP
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind( ('localhost', cmd_line_args['csport']) )
udp_sock.setblocking(False)
sel.register(udp_sock, selectors.EVENT_READ, udp_rgr)

# TCP
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_address = (socket.gethostbyname(socket.gethostname()), cmd_line_args["csport"])
server_address = ('localhost', cmd_line_args['csport'])
tcp_sock.bind(server_address)
print('listening...')
tcp_sock.listen()
tcp_sock.setblocking(False)
sel.register(tcp_sock, selectors.EVENT_READ, tcp_accept)

def sig_handler(sig, frame):
    udp_sock.close()
    tcp_sock.close()
    print("\nExiting Cloud Backup central server...")
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



