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
global last_login
last_login = ()

# deals with an AUT request
# checks users file, responds
def aut(args, user_socket, cred):
    # print(args)
    # message to send back
    response = b'AUR '
    success = False
    username = args[0]
    password = args[1]
    filename = 'user_'+username+'.txt'

    if os.path.isfile(filename):
        # user exists
        with open(filename, 'r+') as f:
            if f.read() == password:
                # user exists and pass is correct
                response += b' OK\n'
                print("User: " + username)
                success = True
            else:
                # user exists and pass is wrong
                response += b' NOK\n'
    else:
        # user doesnt exist yet
        with open(filename, 'w+') as f:   f.write(password)
        os.mkdir(os.path.realpath('')+'/user_'+username)
        response += b' NEW\n'
        print("New user: " + username)
        success = True

        
    # print(users)
    # print(response)
    
    user_socket.sendall(response)
    return success

# deals with a deluser request
def dlu(args, user_socket, cred):
    print('DLU')
    print(cred)

    try:
        userdir = '/user_'+cred[0]
        if os.listdir('.'+userdir):
            # folder not empty
            user_socket.sendall(b'DLR NOK\n')
            return
        # folder empty

        os.remove('user_'+cred[0]+'.txt')
        os.rmdir('.'+userdir)
    except OSError:
        print('Couldnt create modify or delete files in current folder. Check permissions')
        exit()
    
    user_socket.sendall(b'DLR OK\n')

#deals with a dirlist request
def lsd(args, user_socket, cred):
    print('LSD')
    print(cred)

    dirlist = os.listdir('.'+'/user_'+cred[0])
    if not dirlist:
        # dir is empty
        user_socket.sendall(b'LDR 0\n')
        return
    else:
        #dir is not empty
        m = 'LDR '+str(len(dirlist))+' '
        m += ' '.join(dirlist)
        user_socket.sendall(m.encode('utf-8')+b'\n')


#deals with a filelist request
def lsf(args, user_socket, cred):
    print('LSF')
    print(args)

    path = os.getcwd()+'/user_'+cred[0]+'/'+args[0]+'/IP_port.txt'
    with open(path) as f:
        ip = f.read().split()
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = (ip[0], int(ip[1]))
        print(addr)
        cmd = 'LSF '+cred[0]+' '+args[0]+'\n'
        try:
            udp_sock.sendto(cmd.encode('utf-8'), addr)
        except:
            udp_sock.close()
            exit()
        udp_sock.close()
        #falar com bs
        #bs retorna filelist
        #dar esta filelist ao user
        print(f.read())

    user_socket.sendall(b'LFD OK\n')

#deals with a delete request
def delete(args, user_socket, cred):
    print('DEL')
    print(cred)
    user_socket.sendall(b'DDR OK\n')

# #deals with a backup request
# def bck(args, user_socket, cred):
#     print('BCK')
#     print(cred)
#     user_socket.sendall(b'BKK OK\n')

# #deals with a restore request
# def rst(args, user_socket, cred):
#     print('RST')
#     print(cred)
#     user_socket.sendall(b'BKK OK\n')

# get tcp message until \n is found
def get_msg(sock):
    msg = b''
    while True:
        try:
            slic = sock.recv(1024)
            if not slic: 
                msg = b''
                break
            msg += slic
            if msg.find(b'\n') != -1: break
        except socket.error as e:
            print(e)
            exit()
    return msg.decode('utf-8').rstrip('\n')

# TCP session with user
def tcp_session(sock, udp_sock):
    sel.unregister(sock)
    sock.setblocking(True)

    cred = ()

    actions = {
    'AUT':aut,
    'DLU':dlu,
    'LSD':lsd,
    'LSF':lsf,
    'DEL':delete
    }
    while True:
        message = get_msg(sock)
        if not message: break
        args = message.split()
        callable = actions.get(args[0])
        if callable(args[1:], sock, cred):
            cred = (args[1], args[2])


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
tcp_sock.listen(1)
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



