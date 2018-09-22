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
print(args)


def login():
    print("login")
def deluser():
    print("deluser")
def backup():
    print("backup")
def restore():
    print("restore")
def dirlist():
    print("dirlist")
def filelist():
    print("filelist")
def delete():
    print("delete")
def logout():
    print("logout")
def terminate():
    print("terminate")

actions = { 
    'login':login,
    'deluser':deluser,
    'backup':backup,
    'restore':restore,
    'dirlist':dirlist,
    'filelist':filelist,
    'delete':delete,
    'logout':logout,
    'exit':terminate 
}


running = True
while running:
    s = input()
    print(s)


    callable = actions.get(s)
    if callable is None:
        print("I didnt understand the request")
    else:
        callable()


print("hello")

