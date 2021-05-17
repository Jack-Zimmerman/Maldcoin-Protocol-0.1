import socket
import time
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("67.161.43.140", 1234))

headersize = 10
global headercv
global msgdone
global f
global msglen
global finalmsg


finalmsg = ""
f = 0
msgdone = False
headercv = False

def recievemsg():
    global headercv
    global msgdone
    global f
    global msglen
    global finalmsg


    if headercv == False:
        msglen = int(s.recv(10).decode("ISO-8859-1"))
        headercv = True
        msgdone = False
        f = msglen
        recievemsg()
    elif msgdone == False:
        msg = s.recv(10000)
        finalmsg += msg.decode("ISO-8859-1")
        f -= len(msg)
        if f == 0:
            msgdone = True
        recievemsg()
    else:
        f = 0
        headercv = False
        return finalmsg

def fullmsg(message):
    lenbytes = 0
    lenbytes = len(bytes(message, "ISO-8859-1"))
    spaces = ""

    for i in range(10 - len(str(lenbytes))):
        spaces += " "

    fmessage = str(lenbytes) + spaces + message

    return fmessage


class ClientConnection():
	
	def __init__(self, ip, port):
		self.ipconnection = ip
		self.portconnection = port
		self.finalmsg = ""
		s.connect((self.ipconnection, self.portconnection))
	
	def recievemsg(self):
		global headercv
		global msgdone
		global f
		global msglen

		if headercv == False:
			msglen = int(s.recv(10).decode("ISO-8859-1"))
			headercv = True
			msgdone = False
			f = msglen
			self.finalmsg = ""
			recievemsg()
		elif msgdone == False:
			msg = s.recv(10000)
			self.finalmsg += msg.decode("ISO-8859-1")
			f -= len(msg)
			if f == 0:
				msgdone = True
			recievemsg()
		else:
			f = 0
			headercv = False
			return self.finalmsg

	def sendmsg(self, msg):
		s.send(bytes(fullmsg(ske)))
