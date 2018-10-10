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


hostname =  [(s.connect(('10.255.255.255', 1)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
# hostname = '127.0.0.1'
sel = selectors.DefaultSelector()

def aut(args, sock, cred):
    """ Authenticates user received in args.
        username is args[0]. password is args[1]
        
        in: AUT user pass
        
        out: AUR OK or NOK
    """

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
    # print(users)
    # print(response)
    
    sock.sendall(response)
    return success

def upl(args, sock, cred):
    """ Receive backup of dir from user.
        Receives files to backup and puts them in dir
        
        in: UPL dir N (filename date time size data)*
        
        out: UPR OK or NOK
    """

    print(args)


def rsb(args, sock, cred):
    """ Restore dir to user.
        Send files from directory args[0] to user
        
        in: RSB dir
        
        out: RBR N (filename date time size data)*
    """
    print(args)
    path = os.getcwd()+'/user_'+cred[0]+'/'+args[0]
    try:
        files = os.listdir(path)
    except OSError:
        sock.sendall(b'RBR EOF\n')
        return
    resp = 'RBR '+str(len(files))+' '
    resp = resp.encode()
    for file in files:
        filepath = path+'/'+file
        size = str(os.path.getsize(filepath))
        date_time = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(os.path.getmtime(filepath)) )
        with open(filepath, 'rb') as f: data = f.read()
        file_b = ' '.join([file,date_time,size])+' '
        file_b = file_b.encode() + data + b' '
        resp += file_b

    # print(resp)
    sock.sendall(resp)


def get_msg(sock):
    """ Get TCP message until \\n is found"""
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
def tcp_session(sock):
    sel.unregister(sock)
    sock.setblocking(True)

    cred = ()

    actions = {
    'AUT':aut,
    'UPL':upl,
    'RSB':rsb,
    }
    while True:
        message = get_msg(sock)
        if not message: break
        args = message.split()
        callable = actions.get(args[0])
        if callable is None:
            sock.sendall(b'ERR\n')
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




def lsf(args, sock, addr):
    """ List files in dir to CS.
        Send file list from directory args[1] to user args[0]
        
        in: LSF user dir
        
        out: LFD N (filename date time size)*
    """
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


def lsu(args, sock, addr):
    """ Adds user to current users in this server. Requested from CS.
        
        in: LSU user pass
        
        out: LUR OK or NOK or ERR
    """
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



def dlb(args, sock, addr):
    """ Handles directory deletion request from CS.
        Tries to delete directory args[1] for user args[0]
        
        in: DLB user dir
        
        out: DBR OK or NOK
    """
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

try:
    # UDP
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (hostname, cmd_line_args['bsport'])
    # addr = ('localhost', cmd_line_args['bsport'])
    udp_sock.bind( addr )
    udp_sock.setblocking(False)
    sel.register(udp_sock, selectors.EVENT_READ, udp_cs)

    # TCP
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (hostname, cmd_line_args["bsport"])
    # server_address = ('localhost', cmd_line_args['bsport'])
    tcp_sock.bind(server_address)
    print('listening for users...')
    tcp_sock.listen(1)
    tcp_sock.setblocking(False)
    sel.register(tcp_sock, selectors.EVENT_READ, tcp_accept)
except OSError as e:
    print('Error starting the server: '+ str(e))
    exit()

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
        callback(key.fileobj)