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
parser.add_argument('-p', '--csport', type=int, default=58008, help='Central Server port')
args = vars(parser.parse_args())

# debug
print(args)

#Create socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind socket to port

local_hostname = socket.gethostname()
# server_address = (socket.gethostbyname(local_hostname), args["csport"])
server_address = ('localhost', args["csport"])
print("starting up on: %s port: %s" % server_address)
sock.bind(server_address)

# Listen for incoming connections
print('listening...')
sock.listen(1)

# Accept conection
client_sck, client_address = sock.accept()
print('Accepting conection from: ', client_address)

#while True:
    #client_sck, client_address = sock.accept()
    #try:
        #thread.start_new_thread( main, (client_sck, client_address) )
    #except:
        #print "Error: unable to start thread"

# deals with an AUT request
# checks users file, responds
def aut(args):
    # print(args)
    # message to send back
    aur = b'AUR '
    
    with open("users.txt", 'a+') as f:
        f.seek(0)
        users = [value.split() for value in f.readlines()]
        f.read()
        nouser = True
        for value in users:
            if value == args:
                # user exists and password is correct
                aur += b' OK\x00'
                nouser = False
                print("User: " + args[0])
                break
            elif value[0] == args[0]:
                # user exists password is wrong
                aur += b' NOK\x00'
                nouser = False
                break
        
        if nouser:
            #create user in file and return AUR NEW
            aur += b' NEW\x00'
            f.write(args[0]+' '+args[1]+'\n')
            print("New user: " + args[0])
        
    # print(users)
    # print(aur)
    
    client_sck.sendall(aur)

actions = { 
    'AUT':aut
    }

def deal_with_message(msg):
    args = msg.split()
    callable = actions.get(args[0]) # AUT user pass
    callable(args[1:]) # aut( [user,pass] )
   



# Main Loop to user
msg = b''
while True:
    slic = client_sck.recv(16)
    # when remote end is closed and there is no more data the string is empty so we exit loop
    if not slic: break
    msg += slic
    if msg.find(b'\x00') != -1:
        message = msg.strip(b'\x00').decode('utf-8')
        # do something with message
        deal_with_message(message)
        msg = b''
    # n/a


sock.close()
print("Exiting Cloud Backup central server...")