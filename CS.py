#!/usr/bin/python3
import socket
import sys
import multiprocessing
import argparse
import time
import signal

# Redes de Computadores 2018
# Cloud Backup using sockets
# 
# group 8

# Argument Parser for CSname and CSport
parser = argparse.ArgumentParser(description='User Server')
parser.add_argument('-p', '--csport', type=int, default=58008, help='Central Server port')
cmd_line_args = vars(parser.parse_args())


# # Create a UDP socket
# sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# server_address = ('localhost', 58000)
# message = b'This is the message.'

# try:

#     # Send data
#     print('sending...')
#     sent = sock1.sendto(message, server_address)

#     # Receive response
#     print('waiting to receive....')
#     data, server = sock1.recvfrom(4096)
#     print('received {!r}'.format(data))

# finally:
#     print('closing socket')
#     sock1.close()



# deals with an AUT request
# checks users file, responds
def aut(args, user_socket):
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
                aur += b' OK\n'
                nouser = False
                print("User: " + args[0])
                break
            elif value[0] == args[0]:
                # user exists password is wrong
                aur += b' NOK\n'
                nouser = False
                break
        
        if nouser:
            #create user in file and return AUR NEW
            aur += b' NEW\n'
            f.write(args[0]+' '+args[1]+'\n')
            print("New user: " + args[0])
        
    # print(users)
    # print(aur)
    
    user_socket.sendall(aur)

actions = { 
    'AUT':aut
    }

def deal_with_message(msg, user_socket):
    args = msg.split()
    callable = actions.get(args[0]) # AUT user pass
    callable(args[1:], user_socket) # aut( [user,pass] )
   

def deal_with_user(user_socket, user_address):

    print('THIS IS FROM ANOTHER PROCESS')
    time.sleep(2)

    # Main Loop to user
    msg = b''
    while True:
        slic = user_socket.recv(16)
        # when remote end is closed and there is no more data the string is empty so we exit loop
        if not slic: break
        msg += slic
        if msg.find(b'\n') != -1:
            message = msg.strip(b'\n').decode('utf-8')
            # do something with message
            deal_with_message(message, user_socket)
            msg = b''


    print('remote end is closed so closing user_socket')
    user_socket.close()


if __name__ == '__main__':
    
    
    #Create socket TCP/IP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    local_hostname = socket.gethostname()
    # server_address = (socket.gethostbyname(local_hostname), cmd_line_args["csport"])
    server_address = ('localhost', cmd_line_args["csport"])
    print("starting up on: %s port: %s" % server_address)

    # Bind socket to port
    sock.bind(server_address)

    # Listen for incoming connections
    print('listening...')
    sock.listen(1)
    
    
    
    
    
    processes = []

    def sig_handler(sig, frame):
        for p in processes:
            p.join()
        sock.close()
        print("Exiting Cloud Backup central server...")
        exit()
    signal.signal(signal.SIGINT, sig_handler)

    while True:
        # Accept conection from user
        client_sck, client_address = sock.accept()
        print('Accepting conection from: ', client_address)

        p = multiprocessing.Process(target=deal_with_user, args=(client_sck, client_address,))
        processes.append(p)
        p.start()
    
