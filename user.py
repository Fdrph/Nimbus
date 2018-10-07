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
    """ Sends a message to the socket provided and returns the response as a string
        
        sends and receives a string with a newline "\\n" character
        to delimit end of message
    """
    print("sending: " + msg)
    msg += '\n'
    sock.sendall(msg.encode('utf-8'))
    
    msg = b''
    while True:
        slic = sock.recv(1024)
        msg += slic
        if msg.find(b'\n') != -1:
            break

    print("response: " + msg.decode('utf-8'))
    return msg.decode('utf-8').rstrip('\n')


def authenticate(user, passwd, sock):
    """ sends an AUT with user and passwd provided
        
        receives the AUR response and returns the second
        field of it: [OK, NOK, NEW, ERR]
    """
    response = send_msg_sock("AUT"+" "+user+" "+passwd, sock).split()[-1]

    if response == 'NOK':
        print('The password entered is incorrect')
        return False
    if response == 'NEW':
        print('New user has been created')
        return True
    if response == 'OK':
        print('Login was successful')
        return True
    else:
        print('Could not login: ' + response)
        return False

  
def deluser(args, credentials, server_info):

    sock = create_tcp_socket(server_info)

    if not authenticate(credentials['user'], credentials['password'], sock):
        sock.close()
        return
    sock.close()

    sock = create_tcp_socket(server_info)
    response = send_msg_sock('DLU', sock)
    if response == 'DLR NOK':
        print('User deletion not successful: User still has information stored')
    elif response == 'DLR OK':
        print('User deletion successful')
    else:
        print('Unexpected answer: ' + response)

    sock.close()



def backup(args, credentials, server_info):
    #check if dir is listed already in backup_list.txt 
    #if yes check BS_list.txt and ask for the files stored 
    #return files to be updated and the IP and Port of the BS that have the files
    
    print(args)


def restore(args, credentials, server_info):
    print(args)


def dirlist(args, credentials, server_info):
    
    sock = create_tcp_socket(server_info)

    if not authenticate(credentials['user'], credentials['password'], sock):
        sock.close()
        return


    response = send_msg_sock('LSD', sock)
    print(response)

    sock.close()


def filelist(args, credentials, server_info):
    
    sock = create_tcp_socket(server_info)

    if not authenticate(credentials['user'], credentials['password'], sock):
        sock.close()
        return

    response = send_msg_sock('LSF '+args[0], sock)
    print(response)

    sock.close()


def delete(args, credentials, server_info):

    sock = create_tcp_socket(server_info)

    if not authenticate(credentials['user'], credentials['password'], sock):
        sock.close()
        return

    response = send_msg_sock('DEL '+args[0], sock)
    if response == 'DDR OK':
        print('Deletion request was successful')
    elif response == 'DDR NOK':
        print('Deletion request was unsuccessful')

    sock.close()



def terminate(args, credentials={}, server_info={}):
    print('Exiting Cloud Backup..')
    exit()


def login(args, server_info):

    if len(args) < 2:
        print('Missing username and password!')
        return

    if not args[0].isdigit() or not len(args[0]) == 5 or not args[1].isalnum():
        print('User needs to be a 5 digit number and password alphanumeric!')
        return 

    credentials = {"user": args[0], "password": args[1]}

    sock = create_tcp_socket(server_info)

    if not authenticate(credentials["user"], credentials["password"], sock):
        sock.close()
        return
    sock.close()


    actions = { 
        'deluser':deluser,
        'backup':backup,
        'restore':restore,
        'dirlist':dirlist,
        'filelist':filelist,
        'delete':delete,
        'exit':terminate 
    }

    while True:
        print('> ', end='')
        args = input().split()
        callable = actions.get(args[0])
        if args[0] == 'logout':
            break
        elif callable is None:
            print("I didnt understand the request..")
        else:
            if callable(args[1:], credentials, cmd_line_args):  break




actions = { 'login':login, 'exit':terminate }
while True:
    print('> ', end='')
    init = input().split()
    callable = actions.get(init[0])
    if callable is None:
        print("You need to login first!")
    else:
        callable(init[1:], cmd_line_args)
