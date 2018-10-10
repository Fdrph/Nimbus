#!/usr/bin/python3
import socket
import sys
import os
import argparse
import time
import signal
import selectors
import shutil
import random

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


#deals with a backup request
def bck(args, user_socket, cred):
    print(args)
    print(cred)

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.settimeout(2)

    path = os.getcwd()+'/user_'+cred[0]+'/'+args[0]+'/IP_port.txt'
    if not os.path.exists(path):
    # first time
        if not registered_BS:
            print('not bs')
            user_socket.sendall(b'BKR EOF\n')
            return
        bs_ip = random.choice(registered_BS)
        print(bs_ip)
        try:
            udp_sock.sendto(b'LSU '+cred[0].encode()+b' '+cred[1].encode()+b'\n', (bs_ip[0], int(bs_ip[1])) )
            msg, info = udp_sock.recvfrom(8192)
            msg = msg.decode().rstrip('\n').split()
        except OSError:
            print('no resp')
            user_socket.sendall(b'BKR EOF\n')
            return
        finally:
            udp_sock.close()
        if msg[1] == 'NOK':
            print('nok answer')
            user_socket.sendall(b'BKR EOF\n')
            return
        resp = 'BKR '+' '.join(bs_ip)+' '+args[1]+' '+' '.join(args[2:])+'\n'
        # print(resp)
    else:
    # dir has been backed up before
        with open(path) as f:
            bs_ip = f.read().split()
        try:
            udp_sock.sendto(b'LSF '+cred[0].encode()+b' '+args[0].encode()+b'\n', (bs_ip[0], int(bs_ip[1])) )
            msg, info = udp_sock.recvfrom(8192)
            msg = msg.decode().rstrip('\n').split()
        except OSError:
            print('no resp')
            user_socket.sendall(b'BKR EOF\n')
            return
        finally:
            udp_sock.close()
        if msg[1] == 'NOK':
            print('nok answer')
            user_socket.sendall(b'BKR EOF\n')
            return
        print(msg)        
        # Check which files are newer and which havent been backed up yet here
        
        resp = 'BKR EOF\n'   
    user_socket.sendall(resp.encode())



#deals with a restore request
def rst(args, user_socket, cred):
    print('RST')
    print(cred)
    user_socket.sendall(b'BKK OK\n')


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
        user_socket.sendall(m.encode()+b'\n')


#deals with a filelist request
def lsf(args, user_socket, cred):
    print('LSF')
    print(args)

    path = os.getcwd()+'/user_'+cred[0]+'/'+args[0]+'/IP_port.txt'
    if not os.path.exists(path):
        user_socket.sendall(b'LFD NOK\n')
        return
    with open(path) as f:
        bs_ip = f.read().split()
    
    cmd = 'LSF '+cred[0]+' '+args[0]+'\n'
    try:
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.settimeout(1)
        udp_sock.sendto(cmd.encode(), (bs_ip[0], int(bs_ip[1])) )
        msg, info = udp_sock.recvfrom(8192)
    except OSError:
        user_socket.sendall(b'LFD NOK\n')
        return
    finally:
        udp_sock.close()
    
    msg = msg.decode().split()
    msg.insert(2, ' '.join(bs_ip))
    msg = ' '.join(msg) + '\n'
    # print(msg)

    user_socket.sendall(msg.encode())

#deals with a delete directory  request
def delete(args, user_socket, cred):
    print(args)
    print(cred)
    
    path = os.getcwd()+'/user_'+cred[0]+'/'+args[0]+'/IP_port.txt'
    if not os.path.exists(path):
        user_socket.sendall(b'DDR NOK\n')
        return
    with open(path) as f:
        bs_ip = f.read().split()
    
    cmd = 'DLB '+cred[0]+' '+args[0]+'\n'
    try:
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.settimeout(1)
        udp_sock.sendto(cmd.encode(), (bs_ip[0], int(bs_ip[1])) )
        msg, info = udp_sock.recvfrom(8192)
    except OSError:
        user_socket.sendall(b'DDR NOK\n')
        return
    finally:
        udp_sock.close()
    
    msg = msg.decode().split()
    if msg[1] == 'OK':
        path = os.getcwd()+'/user_'+cred[0]+'/'+args[0]
        shutil.rmtree(path, ignore_errors=True)
        user_socket.sendall(b'DDR OK\n')
    else:
        user_socket.sendall(b'DDR NOK\n')


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
    return msg.decode().rstrip('\n')

# TCP session with user
def tcp_session(sock, udp_sock):
    sel.unregister(sock)
    sock.setblocking(True)

    cred = ()

    actions = {
    'AUT':aut,
    'DLU':dlu,
    'BCK':bck,
    'RST':rst,
    'LSD':lsd,
    'LSF':lsf,
    'DEL':delete
    }
    while True:
        message = get_msg(sock)
        if not message: break
        args = message.split()
        callable = actions.get(args[0])
        if callable is None:
            udp_sock.sendall(b'ERR\n')
            break
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
    msg = msg.decode().rstrip('\n').split()
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
try:
    ip =  [(s.connect(('10.255.255.255', 1)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    # UDP socket for bs registration
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind( ('localhost', cmd_line_args['csport']) )
    udp_sock.setblocking(False)
    sel.register(udp_sock, selectors.EVENT_READ, udp_rgr)
    # TCP for user connections
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcp_sock.bind((ip, cmd_line_args['csport']))
    tcp_sock.bind(('localhost', cmd_line_args['csport']))
    tcp_sock.listen(1)
    tcp_sock.setblocking(False)
    sel.register(tcp_sock, selectors.EVENT_READ, tcp_accept)
except OSError as e:
    print('Error starting the server: '+ str(e))
    exit()

def sig_handler(sig, frame):
    udp_sock.close()
    tcp_sock.close()
    print("\nExiting Cloud Backup central server...")
    exit()
signal.signal(signal.SIGINT, sig_handler)

print('listening...')
while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        if callback == tcp_session:
            callback(key.fileobj, udp_sock)
        else:
            callback(key.fileobj)



