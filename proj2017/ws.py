################################################################################
#                             WORKING SERVER                                   #
################################################################################

import socket
import sys
import signal

################################################################################
#                                  VARIAVEIS                                   #
################################################################################
CSname = socket.gethostname()
WSport = 59000
CSport = 58023
MESSAGE = ''
ptc = []
BUFFER = ''
registered = False
tcpOpen = False

################################################################################
#                                   FUNCOES                                    #
################################################################################

def signal_handler(signal, frame):
   """
   Desregista o WS do CS e fecha as comunicaçoes no caso de SIGIINT
   """
   print("*** Working Server is shutting down! ***")
   
   socketUSER.close()
   if registered == True:
      unregisterWS(MESSAGE)
   sys.exit(0)
   
def registerWS(MESSAGE):
   """
   Envia a mensagem de registo do WS e recebe o status do TCP 
   """
   MESSAGE = ''
   MESSAGE = 'REG '
   for i in ptc:
      MESSAGE += i + ' '
   
   MESSAGE += socket.gethostbyname(socket.gethostname()) + ' ' + str(WSport) + '\n'
   
   try:
      s.sendto(MESSAGE.encode(), (CSname, CSport))
   except socket.error:
      print("Erro a enviar!")
      s.close()
      sys.exit(0)  
   
   #verificar tamanho
   try:
      BUFFER, addr = s.recvfrom(1024)
   except socket.error:
      print("Erro a receber!")
      s.close()
      sys.exit(0)
   
   if BUFFER[4:] == 'NOK':
      unregisterWS(MESSAGE)

   return True

def unregisterWS(MESSAGE):
   """
   Envia a mensagem de deregisto do WS, recebe o status do TCP e fecha o UDP
   """
   MESSAGE = ''
   MESSAGE = 'UNR ' + socket.gethostbyname(socket.gethostname()) + ' ' + str(WSport) + '\n'
   
   try:
      s.sendto(MESSAGE.encode(), (CSname, CSport))
   except socket.error:
      print("Erro a enviar!")
      s.close()
      sys.exit(0)
   

   try:
      s.settimeout(1)
      BUFFER, addr = s.recvfrom(1024)
   except socket.error:
      print("Erro a receber!")
      s.close()
      sys.exit(0)

   
def processRequest(ptcCode, filename, size, data):
   """
   Processa o pedido mandado pelo CS e devolve a resposta a ser devolvida pelo WS
   """
   if not isinstance(eval(size), int):
      reply = "REP ERR\n"
      return reply

   reply = ''
   if ptcCode == 'LOW':
      text = ''
      for i in data:
         text += i + ' '
      text = text[:-2]
      print(ptcCode, ":", filename[14:])
      print('  ', size, "bytes received")
      print('  ', filename[14:], str(len(text.encode('utf-8'))), "bytes")
      reply = 'REP F ' + str(len(text.encode('utf-8'))) + ' ' + text.lower() + '\n'
   elif ptcCode == 'UPP':
      text = ''
      for i in data:
         text += i + ' '
      text = text[:-2]
      print(ptcCode, ":", filename[14:])
      print('  ', size, "bytes received")
      print('  ', filename[14:], str(len(text.encode('utf-8'))), "bytes")
      reply = 'REP F ' + str(len(text.encode('utf-8'))) + ' ' + text.upper() + '\n'
      
   elif ptcCode == 'FLW':
      text = ''
      for i in data:
         text += i + ' '
      text = text[:-2]
      parse = text.split()
      longest = parse[0]
      for i in parse:
         if len(i) > len(longest):
            longest = i
      print(ptcCode, ":", filename[14:])
      print('  Longest word:', longest)
      reply = 'REP R ' + str(len(longest.encode('utf-8'))) + ' ' + longest + '\n'
   elif ptcCode == 'WCT':
      count = 0
      text = ''
      for i in data:
         text += i + ' '
      parse = text.split()
      for i in parse:
         if (i[0] >= 'A' and i[0] <= 'Z') or (i[0] >= 'a' and i[0] <= 'z' or (i[0] >= '1' and i[0] <= '9')):
            count += 1
      print(ptcCode, ":", filename[14:])
      print('  Number of words:', str(count))
      reply = 'REP R ' + str(len(str(count))) + ' ' + str(count) + '\n'
   else:
      reply = 'REP EOF\n'
   
   return reply
   

################################################################################
#                                   INICIO                                     #
################################################################################

signal.signal(signal.SIGINT, signal_handler)

for i in range(len(sys.argv)):
   if len(sys.argv[i]) == 3:
      ptc += [sys.argv[i]]
   if sys.argv[i] == '-n':
      CSname = sys.argv[i+1]
   if sys.argv[i] == '-p':
      WSport = eval(sys.argv[i+1])
   if sys.argv[i] == '-e':
      CSport = eval(sys.argv[i+1])
   
try:
   s = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP
except socket.error:
   print("Erro a criar socket!")
   sys.exit(0)

try:
   socketUSER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
   print("Erro a criar socket!")
   unregisterWS(MESSAGE)
   sys.exit(0)


registered = registerWS(MESSAGE)


try:
   socketUSER.bind((socket.gethostbyname(socket.gethostname()), WSport))
except socket.error:
   print("Erro a criar socket!")
   unregisterWS(MESSAGE)
   sys.exit(0)

try:
   socketUSER.listen(1)
except socket.error:
   print("Erro a criar socket!")
   unregisterWS(MESSAGE)
   sys.exit(0)

while True:
   
   try:
      conn, addr = socketUSER.accept()
   except socket.error:
      print("Erro a aceitar socket!")
      unregisterWS(MESSAGE)
      sys.exit(0)   
   
   try:
      BUFFER = conn.recv(1024).decode()
   except socket.error:
      print("Erro a enviar!")
      unregisterWS(MESSAGE)
      socketUSER.close()
      sys.exit(0)   
   
   command = BUFFER.split(' ')
   
   if command[0] == 'WRQ':
      if command[1] in ptc:
         MESSAGE = processRequest(command[1], command[2], command[3], command[4:])
      else:
         MESSAGE = 'REQ EOF\n'
   else:
      MESSAGE = 'ERR\n'

   try:
      conn.send(MESSAGE.encode())
   except socket.error:
      print("Erro a receber!")
      unregisterWS(MESSAGE)
      socketUSER.close()
      sys.exit(0)

conn.close()
tcpOpen = False
unregisterWS(MESSAGE)
