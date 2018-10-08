################################################################################
#                             CENTRAL SERVER                                   #
################################################################################

import socket
import signal
import sys
import select
import os
import glob

################################################################################
#                                   VARIAVEIS                                  #
################################################################################
WSlist = []

################################################################################
#                                   FUNCOES                                    #
################################################################################

def signal_handler(signal, frame):
   print("*** Central Server is shutting down! ***")
   socketUSER.close()
   socketUDP.close()
   sys.exit(0)
   
def findPTC(ptc, lst):
   res = []
   for el1 in lst:
      for el2 in el1[2]:
         if (el2 == ptc):
            res += [[el1[0], el1[1]]]
   return res

def onlySocketsFromList(lst):
   res = []
   for el in lst:
      res += [el[0]]
   return res

def divideFile(filename):
   file = open(filename, 'r')
   lst = []
   lines = file.readlines()
   count = 0
   for line in lines:
      newfile = open("./input_files/" + filename[14:19] + str('%03d'%count) + ".txt" , 'w')
      newfile.write(line)
      newfile.close()
      lst += ["./input_files/" + filename[14:19] + str('%03d'%count) + '.txt'] 
      count += 1
   return lst
   
def doStuffUser(sock, addr, ListWS):
      """
      Le do socket que comunica com o Utilizador
      """
      BUFFER_SIZE = 1024
      bytesReceived = 0
      
      try:
         data = sock.recv(BUFFER_SIZE).decode()
         bytesReceived = len(data)
         parsed = data.split(' ')
         if(parsed[0] == "REQ"):
            while(bytesReceived < eval(parsed[2])):
               data += sock.recv(BUFFER_SIZE).decode()
               parsed = data.split(' ')
               bytesReceived = len(data)
            
      except socket.error:
         print("Erro a receber socketUSER")
         os._exit(0)   
      
      socketWS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      
      message = ""
      
      if(parsed[0] == "LST\n"):
         
         PTClist = []
         PTCstr = ""
         if len(WSlist) > 0:
            for el1 in WSlist:
               for el2 in el1[2]:
                  if el2 not in PTClist:
                     PTClist += [el2]
            PTCstr += str(len(PTClist)) + " "
            for el in PTClist:
               PTCstr += el + " "
         else:
            PTCstr = "EOF"
         message = "FPT " + PTCstr
         print("List request:", addr[0], addr[1])
      elif parsed[0] == "REQ":
         if not os.path.exists('./input_files'):
	         os.makedirs('./input_files')
         fileNumber = 10000
         fileName = "./input_files/" + str(fileNumber) + ".txt"
         while (os.path.exists(fileName)):
            fileNumber += 1
            fileName = "./input_files/" + str(fileNumber) + ".txt"
         file = open(fileName, "w")
         print(fileNumber)
         
         data = ""
         for i in range(3, len(parsed)):
            data += parsed[i] + " "
         
         data = data[:-2] 
         file.write(data)
         file.close()
         
         aux = findPTC(parsed[1], WSlist)

         
         #Cria o diretorio se nao existir
         if not os.path.exists('./output_files'):
	         os.makedirs('./output_files')
         
         #Divide o ficheiro
         files = divideFile(fileName)
         
         WSsockets = []
         res = []
         i = 0
         print(files)
        
         for el in files:
            if i == len(aux):
               i = 0
            newfile = open(el, 'r')
            dataFile = newfile.read()
            MESSAGE = "WRQ " + parsed[1] + " " + el + ' ' + str(len(dataFile)) + ' ' + dataFile + "\n"
            socketWS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socketWS.connect((aux[i][0] , eval(aux[i][1])))
            try:
               socketWS.send(MESSAGE.encode())
            except socket.error:
               print("Erro a enviar para WS")
               os._exit(0)
            WSsockets += [(socketWS, el[14:])]
            i+=1
         
         length = len(WSsockets)
         for i in range(0, len(WSsockets)):
            r, w, e = select.select(onlySocketsFromList(WSsockets), [], [])
            
            filename = "ERROR.txt"
            socketWS = r[0]
            for el in WSsockets:
               if el[0] == r[0]:
                  filename = el[1] 
            #Recebe a data processada
            messageWS = socketWS.recv(BUFFER_SIZE).decode()
            bytesReceived = len(messageWS) 
            parsedWS = messageWS.split(' ')
            
            while(bytesReceived < eval(parsedWS[2])):
               messageWS += socketWS.recv(BUFFER_SIZE).decode()
               bytesReceived = len(mesageWS)
                           
            messageWS = messageWS[:-1]
            parsedWS = messageWS.split(" ")
            res += parsedWS[3:]
            toOutput = ""
            for word in parsedWS[3:]:
               if word[-1] == "\n":
                  toOutput += word
               else:
                  toOutput += word + " "
            outputFile = open("./output_files/" + filename, 'w')
            outputFile.write(toOutput)
            outputFile.close()
            
            socketWS.close()
            WSsockets.remove((socketWS, filename))
            del(r[0])


         if parsed[1] ==  "FLW":
            count = len(res[0])
            word = res[0]
            for el in res:
               if len(el) > count:
                  word = el
                  count = len(el)
            message = word
            outputFile = open("./output_files/" + filename[:5] + ".txt", "w")
            outputFile.write(message)
            outputFile.close()
         elif parsed[1] == "WCT":
            count = 0
            for el in res:
               count += eval(el)
            message = str(count)
            outputFile = open("./output_files/" + filename[:5] + ".txt", "w")
            outputFile.write(message)
            outputFile.close()
         elif parsed[1] == "UPP" or parsed[1] == "LOW":
            message = ''
            for el in files:
               file = open("./output_files/" + el[14:], 'r')
               line = file.read();
               if line[-1] == "\n":
                  message += line
               else:
                  message += line + " "
            message = message[:-2]
            outputFile = open("./output_files/" + filename[:5] + ".txt", "w")
            outputFile.write(message)
            outputFile.close()
                  
         message = "REP " + parsed[1] + " " + parsed[2] + " " + message

      else:
         message = "ERR"

      message += '\n'
      print(">>> ", message)
      sock.send(message.encode())
      sock.close()

def registerWS(lst):
   ptc = []
   i = 0
   while(len(lst[i]) == 3):
      ptc += [lst[i]]
      i += 1
   ws = [lst[i], lst[i+1], ptc]
   return ws

################################################################################
#                                   INICIO                                     #
################################################################################

IP = socket.gethostbyname(socket.gethostname())
PORT = 58023

BUFFER_SIZE = 1024

for i in range(len(sys.argv)):
   if (sys.argv[i] == "-p"):
      PORT = eval(sys.argv[i+1])

signal.signal(signal.SIGINT, signal_handler)

try:
   socketUSER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
   print("Erro a criar socket!")
   sys.exit(0)
   
# Apaga os ficheiros nas pastas
files = glob.glob('./input_files/*.txt')
for f in files:
    os.remove(f)
    
files = glob.glob('./output_files/*.txt')
for f in files:
    os.remove(f)

try:
   socketUSER.bind((IP, PORT))
except socket.error:
   print("Erro a criar socket!")
   sys.exit(0)

try:
   socketUSER.listen(5)
except socket.error:
   print("Erro a criar socket!")
   sys.exit(0)

try:
   socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
   print("Erro a criar socket!")
   sys.exit(0)

try:
   socketUDP.bind((IP, PORT))
except socket.error:
   print("Erro a criar socket!")
   sys.exit(0)


while(True):
   r, w, e = select.select([socketUDP, socketUSER], [], [])

   if socketUSER in r:
      try:
         conn, addr = socketUSER.accept()
      except socket.error:
         print("Erro a aceitar socket!")
         socketUSER.close()
         socketUDP.close()
         sys.exit(0)
      
      pidTCP = os.fork()
      
      if pidTCP < 0:
         print("Erro no fork USER")
         socketUDP.close()
         socketUSER.close()
         conn.close()
         sys.exit(0)
      
      if pidTCP == 0:
         socketUSER.close()
         socketUDP.close()
         doStuffUser(conn, addr, WSlist)
         os._exit(0)
      else:
         conn.close()
         continue
      
      
   
   elif socketUDP in r:
      try:
         data, addr = socketUDP.recvfrom(BUFFER_SIZE)
      except socket.error:
         socketUDP.close()
         socketUSER.close()
         print("Erro a receber")
         
         sys.exit(0)
      parsed = str.split(data.decode())

      if(parsed[0] == "REG"):
         if len(WSlist) < 10:
            ws = registerWS(parsed[1:])
            WSlist += [ws] 
            MESSAGE = "RAK OK\n"
            res = "+ "
            for el in ws[2]:
               res += el + " "
            res += ws[0] + " " + ws[1]
            print(res)
         else:
            MESSAGE = "RAK NOK\n"
            
      
      elif(parsed[0] == "UNR"):
         delete = 0
         ipWS = parsed[1]
         portWS = parsed[2]
         for ws in WSlist:
            if(ws[0] == ipWS and ws[1] == portWS):
               delete = 1
               WSlist.remove(ws)
               MESSAGE = "UAK OK\n"
               res = "- "
               for el in ws[2]:
                  res += el + " "
               res += ipWS + " " + portWS
               print(res)
         if delete == 0:
            MESSAGE = "UAK NOK\n"
      else:
         print("ERR")
         socketUDP.close()
         socketUSER.close()
         sys.exit(0)

      try:
         socketUDP.sendto(MESSAGE.encode(), addr)
      except socket.error:
         print("Erro a receber mensagem")
         socketUDP.close()
         socketUSER.close()
         sys.exit(0)

      
      continue;