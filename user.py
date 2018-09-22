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


def login(args):
    print(args)
def deluser(args):
    print(args)
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
    print(args)

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
    args = input().split()


    callable = actions.get(args[0])
    if callable is None:
        print("I didnt understand the request")
    else:
        callable(args[1:])



