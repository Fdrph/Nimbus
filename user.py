#!/usr/bin/python3
import socket
import sys
import argparse

# Redes de Computadores 2018
# Cloud Backup using sockets
# 
# group 8

# Global variables storing the currently loged in user's
# username and password
username = ''
password = ''

# Argument Parser for CSname and CSport
parser = argparse.ArgumentParser(description='User Server')
parser.add_argument('-n', '--csname', default='localhost', help='Central Server name')
parser.add_argument('-p', '--csport', type=int, default=58008, help='Central Server port')
cmd_line_args = vars(parser.parse_args())
# debug
# print(args)


def create_tcp_socket(server_info):
    """ Creates a TCP socket and returns it

    server_info is a dictionary:
        csname: server host name
        csport: server port

    """
    # Create socket TCP
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except OSError as e:
        print("Unexpected System Call error: "+  e.strerror + "\nExiting Cloud Backup..")
        exit()

    # Connect to server provided in parameter
    server_address = (server_info["csname"], server_info["csport"])
    print("connecting to server: %s port: %d" % server_address)
    try:
        sock.connect(server_address)
    except OSError as e:
        print ("Unexpected System Call error: " + e.strerror + "\nExiting Cloud Backup..")
        exit()

    return sock



def send_msg_sock(msg, sock):
    """ Sends a message to the socket provided and returns the response 
        
        sends and receives a string with a newline "\\n" character
        to delimit end of message
        
        returns a string
    """
    print("sending: " + msg)
    msg += '\n'
    sock.sendall(msg.encode('utf-8'))
    
    msg = b''
    while True:
        slic = sock.recv(16)
        msg += slic
        if msg.find(b'\n') != -1:
            break

    print("response: " + msg.decode('utf-8'))
    return msg.decode('utf-8')


def authenticate(user, passwd, sock):
    response = send_msg_sock("AUT"+" "+user+" "+passwd, sock)
    return response.split()[-1]

  
def deluser(args):
    print(args)

    #conect to server
    #authenticate
    # amnda coisas comandos
    #sock.close
    # if authe
    # print(username+" "+password)



def backup(args):
	#check if dir is listed already in backup_list.txt 
	#if yes check BS_list.txt and ask for the files stored 
	#return files to be updated and the IP and Port of the BS that have the files
	
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
    global username
    username = ''
    global password 
    password = ''

    return True


def terminate(args):

    exit()


def login(args):
    print(args)
    if len(args) < 2:
        print("Missing username and password..")
        return

    global cmd_line_args
    sock = create_tcp_socket(cmd_line_args)


    response = authenticate(args[0], args[1], sock)
    sock.close() # close conection
    if response not in ['OK','NEW']:
        return


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
            if callable(args[1:]):  break


while True:
    init = input().split()
    if init[0] == 'login':
        login(init[1:])
    elif init[0] == 'exit':
        exit()
    else:
        print("You need to login first!")
