#!/usr/bin/python3
import socket
import sys
import os
import time
import argparse
import signal
import selectors
import shutil

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


# hostname =  [(s.connect(('10.255.255.255', 1)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
hostname = '127.0.0.1'
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



# list files in dir provided in args
# args: ['user'. 'directory']
def lsf(args, sock, addr):

    path = os.getcwd()+'/user_'+args[0]+'/'+args[1]
    files = os.listdir(path)
    msg = 'LFD '+str(len(files))+' '
    for file in files:
        filepath = path+'/'+file
        size = str(os.path.getsize(filepath))
        date_time = time.strftime('%d.%m.%Y %H:%M:%S', time.gmtime(os.path.getmtime(filepath)) )
        msg += ' '.join([file,date_time,size]) + ' '

    msg += '\n'
    sock.sendto(msg.encode('UTF-8'), addr)


# handles add user to list from cs
def lsu(args, sock, addr):
    print('LSU: '+str(args))
    username = args[0]
    password = args[1]
    filename = 'user_'+username+'.txt'

    if os.path.isfile(filename):
        # user exists
        sock.sendto(b'LUR NOK\n', addr)
    else:
        # user doesnt exist yet
        with open(filename, 'w+') as f:   f.write(password)
        os.mkdir(os.path.realpath('')+'/user_'+username)
        print("New user: " + username)
        sock.sendto(b'LUR OK\n', addr)


# handles delete dir request from cs
def dlb(args, sock, addr):

    path = os.getcwd()+'/user_'+args[0]+'/'+args[1]
    if not os.path.exists(path):
        sock.sendto(b'DBR NOK\n', addr)
        return
    try:
        shutil.rmtree(path, ignore_errors=True)
        if not os.listdir(os.getcwd()+'/user_'+args[0]):
            # empty
            os.rmdir(os.getcwd()+'/user_'+args[0])
            os.remove(os.getcwd()+'/user_'+args[0]+'.txt')
        sock.sendto(b'DBR OK\n', addr)
    except OSError:
        sock.sendto(b'DBR NOK\n', addr)
        return
    

# handles udp requests from cs
def udp_cs(sock):
    
    actions = {
    'LSF':lsf,
    'LSU':lsu,
    'DLB':dlb
    }
    msg = b''
    msg, addr = sock.recvfrom(8192)
    msg = msg.decode('utf-8').rstrip('\n')
    args = msg.split()
    callable = actions.get(args[0])
    callable(args[1:], sock, addr)

    print(msg)





def register_with_cs():
    cs_addr = (cmd_line_args['csname'], cmd_line_args['csport'])
    rgr = "REG " + hostname + ' ' + str(cmd_line_args['bsport']) + '\n'
    
    try:
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.settimeout(2)
        udp_sock.sendto(rgr.encode('UTF-8'), cs_addr)
        status = udp_sock.recv(1024).decode('UTF-8')
    except OSError as e:
        print('Error Description: '+str(e))
        return False
    finally:
        udp_sock.close()
    
    if status.split()[1] != 'OK':
        return False
   
    return True

if not register_with_cs():
    print("Couldn't register with central server!")
    exit()
else:
    print("Registered sucessfully with central server!")


# UDP
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# addr = (local ip, cmd_line_args['bsport'])
addr = ('localhost', cmd_line_args['bsport'])
udp_sock.bind( addr )
udp_sock.setblocking(False)
sel.register(udp_sock, selectors.EVENT_READ, udp_cs)

# TCP
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_address = (hostname, cmd_line_args["csport"])
server_address = ('localhost', cmd_line_args['bsport'])
tcp_sock.bind(server_address)
print('listening for users...')
tcp_sock.listen(1)
tcp_sock.setblocking(False)
sel.register(tcp_sock, selectors.EVENT_READ, tcp_accept)


# Receives ctrl^C and sends unregister
# request to CS, exits afterwards
def sig_handler(sig, frame):
    udp_sock.close()
    tcp_sock.close()
    udp_sock.setblocking(True)

    snd = 'UNR '+hostname+' '+str(cmd_line_args['bsport'])+'\n'
    try:
        t_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        t_sock.settimeout(0.5)
        t_sock.sendto(snd.encode('UTF-8'), (cmd_line_args['csname'], cmd_line_args['csport']) )
        msg = t_sock.recv(1024).decode('UTF-8').rstrip('\n')
        if msg != 'UAR OK': print("\nCouldn't unregister with central server!")
    except OSError:
        print("\nCouldn't unregister with central server!")
    finally:
        t_sock.close()
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
