import socket
import time
import threading
from requests import get

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def grabPublicIp():
    ip = get('https://api.ipify.org').text
    return ip

def grabPrivateIp():
    return (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]


# Adds the header to a message to be sent
def fullmsg(message):
    lenbytes = len(bytes(message, "utf-8"))
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
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


        self.clientSocket.connect((self.ipconnection, self.portconnection))

        print("Connected")
        self.finalmsg = ""
        self.dataRecieved = 0
        self.msgDone = False
        self.headerRcv = False


    def recievemsg(self):
        if self.headerRcv == False:
            self.finalmsgS = ""
            try:
                self.numConnection = int(self.clientSocket.recv(10).decode("utf-8"))
                self.headerRcv = True
                self.msgDone = False
                self.recievemsg()
            except:
                return
        elif self.msgDone == False:
            msg = self.clientSocket.recv(10)
            self.finalmsg += msg.decode("utf-8")
            self.numConnection -= len(msg)
            if self.numConnection == 0:
                self.msgDone = True
            self.recievemsg()
        else:
            self.numConnection = 0
            self.headerRcv = False
            return


    def sendmsg(self, msg):
        self.clientSocket.send(bytes(fullmsg(msg)))


    def recieverealtime(self):
        while True:
            self.recievemsg()
            print(self.finalmsg)

# TCP Server
class Server():
    def __init__(self, hosting_ip, port, num_connections):

        self.hosting_ip = hosting_ip
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((hosting_ip, port))
        self.s.listen(num_connections)

        self.finalmsg = ""
        self.headercv = False
        self.msgdone = False
        self.datarcv = 0


        self.connections = []
        self.clientConnections = []
        self.numTotalConnections = 0
        self.numCurrentConnections = 0
        self.dataRecievedPerUser = []

        print("$Iniated Server at " + str(self.hosting_ip) + "\n")

    def acceptconnections(self, printOut = True, output = ""):

        clientsocket, address = self.s.accept()
        print("$New connection from: " + str(address[0]) + "\n")

        self.numTotalConnections += 1
        self.connections.append([clientsocket, address])
        if printOut == True:
            print(self.connections[-1][1])



    def sendataspecfic(self, data, clientsocket):
            clientsocket.send(bytes(fullmsg(data), "utf-8"))

    def sendata(self, data):
        while True:
            self.s.send(bytes(fullmsg(data), "utf-8"))

    def recievemsg(self, clientsocket):
        global headercv1
        global msgdone1
        global j

        if self.headercv == False:
            self.finalmsg = ""
            try:
                self.datarcv = int(clientsocket.recv(10).decode("utf-8"))
                self.headercv = True
                self.msgdone = False
                self.recievemsg(clientsocket)
            except:
                return
        elif self.msgdone == False:
            msg = clientsocket.recv(10)
            self.finalmsg += msg.decode("utf-8")
            self.datarcv -= len(msg)
            if self.datarcv == 0:
                self.msgdone = True
            self.recievemsg(clientsocket)
        else:
            self.datarcv = 0
            self.headercv = False

    def closeConnection(self, clientSocket):
        clientSocket.close()




#end
