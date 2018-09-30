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
parser.add_argument('-n', '--csname', default='localhost', help='Central Server name')
parser.add_argument('-p', '--csport', type=int, default=58008, help='Central Server port')
args = vars(parser.parse_args())

# debug
# print(args)

# Create socket TCP/IP
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except OSError as e:
    print("Unexpected System Call error: "+  e.strerror + "\nExiting Cloud Backup..")
    exit()

# Connect to server
server_address = (args["csname"], args["csport"])
print("connecting to central server: %s port: %d" % server_address)
try:
    sock.connect(server_address)
except OSError as e:
    print ("Unexpected System Call error: " + e.strerror + "\nExiting Cloud Backup..")
    exit()
    

username = ''
password = ''



def send_to_cs(msg):
    """ Sends a message to the central server and returns the response 
        
        receives a string with a null "\\0" character 
        
        returns a string
    """
    print("sending: " + msg)
    sock.sendall(msg.encode('utf-8'))

    msg = b''
    while True:
        slic = sock.recv(16)
        msg += slic
        if msg.find(b'\x00') != -1:
            break

    print("response: " + msg.decode('utf-8'))
    return msg.decode('utf-8')


def authenticate(user, passwd):
    response = send_to_cs("AUT"+" "+user+" "+passwd+"\0")
    return response.split()[-1]



    

def deluser(args):
    print(args)
    # if authe
    # print(username+" "+password)



def backup(args):
    print(args)


def restore(args):
    print(args)


def dirlist(args):
    print(args)


def filelist(args):
    print(args)


def delete(args):
    print(args)


def logout(args):
    print(args)


def terminate(args):

    exit()
    print(args)


def login(args):
    print(args)
    if len(args) < 2:
        print("Missing username and password..")
        return

    response = authenticate(args[0], args[1])
    print(response)

    global username
    username = args[0]
    global password 
    password = args[1]

    actions = { 
        'deluser':deluser,
        'backup':backup,
        'restore':restore,
        'dirlist':dirlist,
        'filelist':filelist,
        'delete':delete,
        'logout':logout,
        'exit':terminate 
    }

    while True:
        args = input().split()
        callable = actions.get(args[0])
        if callable is None:
            print("I didnt understand the request..")
        else:
            callable(args[1:])


while True:
    init = input().split()
    if init[0] == 'login':
        login(init[1:])
    else:
        print("I didnt understand the request..")
