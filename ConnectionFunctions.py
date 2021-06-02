import socket
import time
import threading
from requests import get

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

headersize = 10
msglen = 0
finalmsg = ""

# For the client recieve recursion
f = 0
msgdone = False
headercv = False

# For the connection dictionary numaration
h = 1

# For the server recieve recursion
j = 0
msgdone1 = False
headercv1 = False

def grabPublicIp():
    ip = get('https://api.ipify.org').text
    return ip

def grabPrivateIp():
    return (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]


# Adds the header to a message to be sent
def fullmsg(message):
    lenbytes = len(bytes(message, "ISO-8859-1"))
    spaces = ""

    for i in range(10 - len(str(lenbytes))):
        spaces += " "

    fmessage = str(lenbytes) + spaces + message

    return fmessage


# TCP Client Connection
class ClientConnection():
    def __init__(self, ip, port):
        self.ipconnection = ip
        self.portconnection = port
        self.finalmsg = ""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.ipconnection, self.portconnection))
        print("Connected")

    def recievemsg(self):
        global headercv
        global msgdone
        global f
        global msglen

        if headercv == False:
            f = int(self.s.recv(10).decode("ISO-8859-1"))
            headercv = True
            msgdone = False
            self.finalmsg = ""
            self.recievemsg()
        elif msgdone == False:
            msg = self.s.recv(10000)
            self.finalmsg += msg.decode("ISO-8859-1")
            f -= len(msg)
            if f == 0:
                msgdone = True
            self.recievemsg()
        else:
            f = 0
            headercv = False
            return self.finalmsg

    def sendmsg(self, msg):
        self.s.send(bytes(fullmsg(self.msg)))

    def recieverealtime(self):
        while True:
            self.recievemsg()
            print(self.finalmsg)


# TCP Server
class Server():
    def __init__(self, hosting_ip, port, num_connections):
        self.hosting_ip = hosting_ip
        self.port = port
        s.bind((hosting_ip, port))
        s.listen(num_connections)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = {}
        self.finalmsgS = ""
        print("Iniated Server at " + str(self.hosting_ip))

    def acceptconnections(self):
        global h

        while True:
            clientsocket, address = s.accept()
            self.connections["Connection" + str(h)] = [clientsocket, address]
            print(self.connections["Connection" + str(h)][1])
            h += 1

    def sendataspecfic(self, data, clientsocket):
            clientsocket.send(bytes(fullmsg(data), "utf-8"))

    def sendata(self, data):
        while True:
            self.s.send(bytes(fullmsg(data), "utf-8"))

    def recievemsg(self, clientsocket):
        global headercv1
        global msgdone1
        global j

        if headercv1 == False:
            self.finalmsgS = ""
            try:
                j = int(clientsocket.recv(10).decode("utf-8"))
                headercv1 = True
                msgdone1 = False
                self.recievemsg(clientsocket)
            except:
                return

        elif msgdone1 == False:
            msg = clientsocket.recv(10)
            self.finalmsgS += msg.decode("utf-8")
            j -= len(msg)
            if j == 0:
                msgdone1 = True
            self.recievemsg(clientsocket)
        else:
            j = 0
            headercv1 = False
	


#print("lol")
#clientTest = ClientConnection("67.161.43.140", 1234)


#clientTest.sendmsg("00000000000000000000000000000000BALANCE00000000000000000000000000000000024b65688de063e9144bb349622e4f914cb01c760dec160e83c22ab979fefe30dc")

#clientTest.recievemsg()

#print(clientTest.finalmsg)
"""
connection = ClientConnection("67.161.43.140",1234)
"""

#end
