################################################################################
#                             USER APPLICATION                                 #
################################################################################
import socket
import sys
import signal
import os

def signal_handler(signal, frame):
   print("*** User is shutting down! ***")
   s.close()
   sys.exit(0)


################################################################################
#                                   INICIO                                     #
################################################################################

signal.signal(signal.SIGINT, signal_handler)

try:
   TCP_IP = socket.gethostbyname(socket.gethostname())
except socket.error:
   print("Erro a obter IP a que vai ligar")
   sys.exit

TCP_PORT = "58023"
BUFFER_SIZE = 1024
flagExit = 1
ptc = ""
bytesToSend = 0
bytesReceived = 0

for i in range(len(sys.argv)):
   if (sys.argv[i] == "-n"):
      TCP_IP = socket.gethostbyname(sys.argv[i+1])
   if (sys.argv[i] == "-p"):
      TCP_PORT = sys.argv[i+1]

while (flagExit):
   try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   except socket.error:
      print("Erro a criar socket!")
      sys.exit(0)

   toRead = input("> ")
   scan = str.split(toRead)
   if (scan[0] == "exit"):
      flagExit = 0
      break
   elif (scan[0] == "list"):
      message = "LST" + "\n"
   elif (scan[0] == "request" and len(scan) == 3):
      ptc = scan[1]
      if not os.path.isfile(scan[2]):
         print("Unknown file")
         break
      else:
         f = open(scan[2])
         text = f.read()
         bytesToSend = len(text.encode("utf-8"))
         f.close()
         message = "REQ " + ptc + " " + str(bytesToSend) + " " + text + "\n"
   else:
      print("Unknown command!")
      continue

   try:
      s.connect((TCP_IP,eval(TCP_PORT)))
   except socket.error:
      print("Erro a ligar ao servidor!")
      s.close()
      sys.exit(0)
   
   if ptc == "UPP" or ptc == "LOW":
      print("" + str(bytesToSend) + " Bytes to transmit")
      
   try:
      bytesSent = s.send(message.encode())
   except socket.error:
      print("Erro a enviar mensagem!")
      s.close()
      sys.exit(0)

   try:
      data = s.recv(BUFFER_SIZE).decode()

      while(data[-1] != "\n"):
         data += s.recv(BUFFER_SIZE).decode()
   except socket.error:
      print("Erro a receber mensagem!")
      s.close()
      sys.exit(0)
   
   data = data[:-1]
   dataParsed = data.split(' ')
   res = ''

   if dataParsed[0] == "FPT" and dataParsed[1] == "EOF":
      res = "No servers available\n"
  
   elif dataParsed[0] == "FPT":
      i = 0
      for i in range(eval(dataParsed[1])):
         if dataParsed[i+2] == "FLW":
            res += '  ' + str(i+1) + "- " + dataParsed[i+2] + " - find longest word" + "\n"
         elif dataParsed[i+2] == "WCT":
            res += '  ' + str(i+1) + "- " + dataParsed[i+2] + " - word count" + "\n"
         elif dataParsed[i+2] == "UPP":
            res += '  ' + str(i+1) + "- " + dataParsed[i+2] + " - convert to upper case" + "\n"
         elif dataParsed[i+2] == "LOW":
            res += '  ' + str(i+1) + "- " + dataParsed[i+2] + " - convert to lower case" + "\n"
         else:
            res = "FPT ERR"
            print(res)
            s.close()
            sys.exit(0)
            
   elif dataParsed[0] == "REP":
      if ptc == "WCT":
         res += "    Number of words: " + dataParsed[3]   
      elif ptc == "FLW":
         res += "    Longest word: " + dataParsed[3]
      elif ptc == "UPP" or ptc == "LOW":
         res += "    received " + dataParsed[2] + " Bytes\n"
         for el in dataParsed[3:]:
            res += el + " " 
      else:
         res = "REP EOF"
         print(res)
         s.close()
         sys.exit(0)
            
   
   else:      
      res = "ERR"
      print(res)
      s.close()
      sys.exit(0)
   
   res += '\n'
   print(res)
   s.close()