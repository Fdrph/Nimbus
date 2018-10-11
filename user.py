#!/usr/bin/python3
import socket
import sys
import argparse
import os
import time

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
        if not slic:
            print('Cloud Backup Server has disconnected!')
            exit()
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
    """ Delete user from CS
        Try to delete user from CS, user is deleted if no information is stored
        for this user

        out:    DLU

        in:     DLR OK or NOK
    """
    sock = create_tcp_socket(server_info)

    if not authenticate(credentials['user'], credentials['password'], sock):
        sock.close()
        return

    success = False

    response = send_msg_sock('DLU', sock)
    if response == 'DLR NOK':
        print('User deletion not successful\nUser still has information stored')
    elif response == 'DLR OK':
        print('User deletion successful\nLogging out..')
        success = True
    else:
        print('Unexpected answer: ' + response)

    sock.close()
    return success


def save_files(data, directory):
    path = os.getcwd()+'/'+directory
    if not os.path.exists(path):
        os.mkdir(path)

    def rd_to_space(data):
        val = ''
        for byte in data:
            if byte==32: break #32=space
            val += chr(byte)
        data = data[len(val)+1:] #remove what we read
        # print(val)
        return val, data

    N, data = rd_to_space(data)
    N = int(N)  #number of files
    # FOR EACH FILE
    for i in range(0, N):
        filename, data = rd_to_space(data)
        t1, data = rd_to_space(data)
        t2, data = rd_to_space(data)
        size, data = rd_to_space(data)
        size = int(size)
        file = data[:size]
        with open(path+'/'+filename, 'wb') as f: f.write(file)
        print(t1+' '+t2)
        t = time.mktime(time.strptime(t1+' '+t2, '%d.%m.%Y %H:%M:%S'))
        os.utime(path+'/'+filename, (t,t))
        data = data[size+1:]


    # print(data)


def backup(args, credentials, server_info):
    """ Backup directory.
        Gets BS info and which files to send from CS. Uploads these files to BS
        
        out to cs:  BCK dir N (filename date time size)*

        in:         BKR ipBS portBS N (filename date time size)*

        out to bs:  UPL dir N (filename date time size data)*
        
        in:         UPR OK or NOK
    """
    directory = args[0]
    # AUT with CS
    sock = create_tcp_socket(server_info)
    if not authenticate(credentials['user'], credentials['password'], sock):
        sock.close()
        return

    path = os.getcwd()+'/'+directory
    if not os.path.isdir(path):
        print('Directory does not exist')
        sock.close()
        return
    files = os.listdir(path)
    if not files:
        print('Directory is empty')
        socket.close()
        return

    msg = 'BCK '+directory+' '+str(len(files))+' '
    for file in files:
        filepath = path+'/'+file
        size = str(os.path.getsize(filepath))
        date_time = time.strftime('%d.%m.%Y %H:%M:%S', time.gmtime(os.path.getmtime(filepath)) )
        msg += ' '.join([file,date_time,size]) + ' '

    # Ask CS for files to UPL
    response = send_msg_sock(msg, sock).split()
    sock.close()
    if response[1] == 'EOF':
        print('BS responded with an error')
        return
    if response[3] == '0':
        print('No more files need backup')
        return
    # print(response)
    # Now we talk to BS
    # AUT with BS
    bs_sock = create_tcp_socket({"csname":response[1], "csport":int(response[2])})
    if not authenticate(credentials['user'], credentials['password'], bs_sock):
        sock.close()
        return
    files = [x for x in files if x in response]
    tosend = 'UPL '+directory+' '+str(len(files))+' '
    tosend = tosend.encode()
    for file in files:
        filepath = path+'/'+file
        size = str(os.path.getsize(filepath))
        date_time = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(os.path.getmtime(filepath)) )
        with open(filepath, 'rb') as f: data = f.read()
        file_b = ' '.join([file,date_time,size])+' '
        file_b = file_b.encode() + data + b' '
        tosend += file_b
    # print(tosend)
    
    bs_sock.sendall(tosend)
    resp = bs_sock.recv(8192).decode().rstrip('\n')
    if resp == 'UPR NOK':
        print('Could not backup directory!')
    else:
        print('completed - '+directory+': ', end='')
        [print(' '+x, end='') for x in files]
        print()
    bs_sock.close()



def restore(args, credentials, server_info):
    """ Restore Directory.
        Get BS info from CS, then get files from BS for dir provided
        
        out to cs:  RST dir

        in:         RSR ipBS portBS

        out to bs:  RSB dir
        
        in:         RBR N (filename date time size data)*
    """

    # we ask the cs for bs ip and port
    sock = create_tcp_socket(server_info)
    if not authenticate(credentials['user'], credentials['password'], sock):
        sock.close()
        return
    response = send_msg_sock('RST '+args[0], sock).split()
    sock.close()
    if response[1] == 'EOF' or response[1] == 'ERR':
        print("Cant restore this directory")
        return
    # now we talk to bs
    bsname = response[1]
    bsport = response[2]
    bs_sock = create_tcp_socket({"csname":bsname, "csport":int(bsport)})
    if not authenticate(credentials['user'], credentials['password'], bs_sock):
        print("Couldn't authenticate with BS!")
        bs_sock.close()
        return

    tosend = 'RSB '+args[0]+'\n'
    bs_sock.sendall(tosend.encode())
    resp = b''
    while True:
        slic = bs_sock.recv(8192)
        resp += slic
        if len(slic)<8192:
            break
    bs_sock.close()
    # print(resp)
    if resp == b'RBR EOF\n':
        print("Couldn't receive files from BS!")
        return
    resp = resp[4:] # remove 'RGR '
    save_files(resp, args[0])

    # print(resp)







def dirlist(args, credentials, server_info):
    """ List all directories.
        
        out to cs:  LSD

        in:         LDR N (dirname)*
    """
    sock = create_tcp_socket(server_info)

    if not authenticate(credentials['user'], credentials['password'], sock):
        sock.close()
        return

    response = send_msg_sock('LSD', sock).split()
    sock.close()
    if response[1] == '0':
        print('There are no directories to list')
        return
    print(' '.join(response[2:]))


def filelist(args, credentials, server_info):
    """ List all files in directory.
        
        out:    LSF dir

        in:     LFD BSip BSport N (filename date time size)*
    """
    sock = create_tcp_socket(server_info)

    if not authenticate(credentials['user'], credentials['password'], sock):
        sock.close()
        return

    res = send_msg_sock('LSF '+args[0], sock).split()
    sock.close()

    if res[1] == 'NOK':
        print("Folder doesn't exist")
        return

    print('BS: '+' '.join(res[2:4])+'\n')
    res = res[4:]
    for i in range(0,len(res),4):
        print(res[i]+' '+res[i+1]+' '+res[i+2]+' '+res[i+3])


def delete(args, credentials, server_info):
    """ Delete specified folder
        
        out:    DEL dir

        in:     DDR OK or NOK
    """
    if len(args) < 1:
        print('Must provide a folder to delete')
        return
    
    sock = create_tcp_socket(server_info)
    if not authenticate(credentials['user'], credentials['password'], sock):
        sock.close()
        return

    response = send_msg_sock('DEL '+args[0], sock)
    sock.close()
    if response == 'DDR OK':
        print('Deletion request was successful')
    elif response == 'DDR NOK':
        print('Deletion request was unsuccessful')


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
