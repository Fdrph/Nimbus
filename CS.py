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



def deal_with_message(msg, user_socket):
    actions = { 
    'AUT':aut
    }
    args = msg.split()
    callable = actions.get(args[0]) # AUT user pass
    callable(args[1:], user_socket) # aut( [user,pass] )
   

def deal_with_user(user_socket, user_address, udp_sock):
    data, server = udp_sock.recvfrom(1024)
    print('received {!r}'.format(data))
    print('THIS IS FROM ANOTHER PROCESS')
    time.sleep(5)

    # Main Loop to user
    msg = b''
    while True:
        slic = user_socket.recv(1024)
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

def deal_with_bs(cmd_line_args, udp_sock):
    print('')
    # # Create a UDP socket
    # sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # server_address = ('localhost', cmd_line_args['csport'])
    # sock1.bind(server_address)

    def sig_handler(sig, frame):
        print("Exiting UDP child process -> SIGINT...")
        exit()
    signal.signal(signal.SIGINT, sig_handler)

    data, server = udp_sock.recvfrom(1024)
    print('received {!r}'.format(data))

    # try:

    #     # Send data
    #     print('sending...')
    #     sent = sock1.sendto(message, server_address)

    #     # Receive response
    #     print('waiting to receive....')
    #     data, server = sock1.recvfrom(1024)
    #     print('received {!r}'.format(data))

    # finally:
    #     print('closing socket')
    #     sock1.close()

if __name__ == '__main__':
    
    # Create a UDP socket
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ('localhost', cmd_line_args['csport'])
    udp_sock.bind(server_address)

    # data, server = sock1.recvfrom(1024)
    # print('received {!r}'.format(data))


    # Create socket TCP/IP to listen to users
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    local_hostname = socket.gethostname()
    # server_address = (socket.gethostbyname(local_hostname), cmd_line_args["csport"])
    server_address = ('localhost', cmd_line_args["csport"])
    print("starting up on: %s port: %s" % server_address)

    # Bind socket to port
    tcp_sock.bind(server_address)

    # Listen for incoming connections from users
    print('listening...')
    tcp_sock.listen(1)
    
    
    
    
    
    processes = []

    def sig_handler(sig, frame):
        print("Exiting Cloud Backup central server...")
        for p in processes:
            p.join()
        tcp_sock.close()
        # delete BS file here
        exit()
    signal.signal(signal.SIGINT, sig_handler)

    pbs = multiprocessing.Process(target=deal_with_bs, args=(cmd_line_args, udp_sock,))
    processes.append(pbs)
    pbs.start()
    while True:
        # Accept conection from user
        client_sck, client_address = tcp_sock.accept()
        print('Accepting conection from: ', client_address)

        p = multiprocessing.Process(target=deal_with_user, args=(client_sck, client_address, udp_sock,))
        processes.append(p)
        p.start()
    
