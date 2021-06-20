# text encoding is in ISO-8859-1

# grabbing blockchain external functions:
from blockchainFunctions import stringHash
from blockchainFunctions import rawHash
from blockchainFunctions import addHash
from blockchainFunctions import arbDifficulty
from blockchainFunctions import verifyBlock
from blockchainFunctions import verifyTransaction
from blockchainFunctions import nodeVerifyTransaction
from blockchainFunctions import generateBalance
from blockchainFunctions import mine

# grabbing blockchain external classes:
from blockchainFunctions import inputPassword
from blockchainFunctions import wallet
from blockchainFunctions import blockChain
from blockchainFunctions import transaction
from blockchainFunctions import block

# grabbing network protocol external functions:
from ConnectionFunctions import fullmsg
from ConnectionFunctions import grabPublicIp

# grabbing network protocol external classes:
from ConnectionFunctions import ClientConnection
from ConnectionFunctions import Server

# pip libraries
import hashlib
import merklelib

import time
import json
import ecdsa
import codecs
import cryptocode
import zlib, base64
import socket
import threading

blockchain = blockChain()
blockchain.syncChain()

pendingTransactions = []


def writeKnownData():
    global blockchain
    knownAccounts = []

    data = {"bals": {}, "noncesUsed": {}}

    for x in blockchain.chainDict:
        for y in x["transactions"]:
            for z in y["outputs"]:
                if z[0] not in knownAccounts:
                    knownAccounts.append(z[0])

    for account in knownAccounts:
        nonces = []

        for y in blockchain.chainDict:
            for z in y["transactions"]:
                if (z["sender"] == account):
                    nonces.append(int(z["nonce"], 16))

        data["noncesUsed"][account] = nonces

    for account in knownAccounts:
        data["bals"][account] = generateBalance(blockchain, account)

    with open("knownData.dat", "w") as knownFile:
        knownFile.write(json.dumps(data, indent=4))


class nodeCommand:
    def __init__(self, node):
        self.node = node

    def handleRequest(self, request):
        self.request = request
        try:
            if self.request.startswith("00000000000000000000000000000000GETCHAINDATA00000000000000000000000000000000"):
                return self.getchaindata()
            elif self.request.startswith("00000000000000000000000000000000TRANSACTION00000000000000000000000000000000"):
                return self.recieveTransaction()
            elif self.request.startswith("00000000000000000000000000000000BALANCE00000000000000000000000000000000"):
                return self.returnBalance()
            elif self.request.startswith("00000000000000000000000000000000BLOCK00000000000000000000000000000000"):
                return self.addBlock()
            elif self.request.startswith(
                    "00000000000000000000000000000000LISTRANSACTIONS00000000000000000000000000000000"):
                return self.listTransactions()
            elif self.request.startswith(
                    "00000000000000000000000000000000GETBLOCKCOUNT00000000000000000000000000000000"):
                return blockchain.size
            elif self.request.startswith("00000000000000000000000000000000DIFFICULTY00000000000000000000000000000000"):
                return blockchain.chainDict[-1]["difficulty"]
        except:
            return "INVALID_REQUEST"

    def getchaindata(self):
        global blockchain

        request = json.loads(
            self.request.replace("00000000000000000000000000000000GETCHAINDATA00000000000000000000000000000000", ""))

        return blockchain.chainDict[request[0]: request[1]]
        # returns blockchain data from block of height index1 to block of height index2

    def recieveTransaction(self):
        global blockchain
        grabbedTransaction = json.loads(
            self.request.replace("00000000000000000000000000000000TRANSACTION00000000000000000000000000000000", ""))

        if verifyTransaction(blockchain, grabbedTransaction):
            pendingTransactions.append(grabbedTransaction)
            for i in range(len(self.node.server.connections)):
                self.node.server.sendataspecfic("00000000000000000000000000000000TRANSACTION00000000000000000000000000000000" + str(grabbedTransaction), self.node.server.connections.values()[i][0])
            return "ACCEPTED" + grabbedTransaction["txhash"]

        else:
            return "DECLINED" + grabbedTransaction["txhash"]

    def returnBalance(self):
        global blockchain

        account = self.request.replace("00000000000000000000000000000000BALANCE00000000000000000000000000000000", "")

        return generateBalance(blockchain, account)

    def addBlock(self):
        global blockchain

        grabbedBlock = json.loads(
            self.request.replace("00000000000000000000000000000000BLOCK00000000000000000000000000000000", ""))

        if verifyBlock(grabbedBlock):
            # add block to chain and disperse
            for i in range(len(self.node.server.connections)):
                self.node.server.sendataspecfic(grabbedBlock,self.node.server.connections.values()[i][0])
            return "ACCEPTED" + grabbedBlock["header"]
        else:
            return "DECLINED" + grabbedBlock["header"]

    def listTransactions(self):
        global blockchain

        account = self.request.replace(
            "00000000000000000000000000000000LISTRANSACTIONS00000000000000000000000000000000", "")

        tiedTransactions = []

        for x in blockchain.chainDict:
            for y in x["transactions"]:
                if y["sender"] == account:
                    tiedTransactions.append(y)
                else:
                    for output in y["outputs"]:
                        if (output[0] == account):
                            tiedTransactions.append(y)
                            break

        return tiedTransactions


class FullNode():

    def __init__(self, hostingIPAdress):
        self.hostingIPAdress = hostingIPAdress
        self.server = Server(hostingIPAdress, 1234, 5)
        self.consoleOutputInfo = ""

    def consoleOutput(self):

        # Defining the thread
        def consoleOutputThread():
            while True:
                if self.consoleOutputInfo != "":
                    print(str(self.consoleOutputInfo))
                    self.consoleOutputInfo = ""


        # Threading Console Output
        consoleOutputThread = threading.Thread(target=consoleOutputThread)
        consoleOutputThread.start()

    def accecptConnections(self):

        # Defining the thread
        def acceptConnectionsThread():
            while True:

                self.server.acceptconnections(False, self.consoleOutputInfo)
                self.server.numCurrentConnections = len(self.server.connections)
                #addressesToPrint = list(self.server.connections.values())
                #self.consoleOutputInfo = addressesToPrint[-1]

        # Threading the connection acceptor
        acceptingConnectionsThread = threading.Thread(target=acceptConnectionsThread)
        self.consoleOutputInfo = "\nAccepting Connections\n"
        acceptingConnectionsThread.start()

    def handleRequests(self):

        # Defining the thread
        def handleRequestsThread():
            while True:
                connectionsList = list(self.server.connections.values())
                for i in range(len(connectionsList)):
                    try:
                        self.server.recievemsg(connectionsList[i][0])
                        request = nodeCommand(self)
                        toReturn = request.handleRequest(self.server.finalmsgS)
                        self.server.sendataspecfic(toReturn, connectionsList[i][0])
                        self.consoleOutputInfo = str(toReturn) + str(connectionsList[i][1])
                    except:
                        pass

        # Threading Handle Requests
        handleRequestsThread = threading.Thread(target=handleRequestsThread)
        self.consoleOutputInfo = "Proccesing Requests\n"
        handleRequestsThread.start()



# Server Start:

fullNodeServer = FullNode("10.0.0.35")

fullNodeServer.consoleOutput()
fullNodeServer.accecptConnections()
fullNodeServer.handleRequests()



"""
def requestHandler():
	while True:
		for i in range(len(fullNodeServer.connections)):
			fullNodeServer.recievemsg(fullNodeServer.connections["Connection" + str((i + 1))][0])
			request = handleRequest(fullNodeServer.finalmsgS)
			toReturn = request.handleRequest()
			fullNodeServer.sendataspecfic(toReturn,fullNodeServer.connections["Connection" + str((i + 1))][0])
acceptConnectionsThread = threading.thread(target=fullNodeServer.acceptconnections)
requestHandlerThread = threading.thread(target=requestHandler)
acceptConnectionsThread.start()
requestHandlerThread.start()
"""
"""
fullNodeServer.acceptconnections()
time.sleep(1)
#Connection Tester
while True:
    fullNodeServer.recievemsg(fullNodeServer.connections[1][0])
    try:
        fullNodeServer.s.connect((grabPublicIp(), 1234))
        fullNodeServer.sendataspecfic(1, fullNodeServer.connections[1][0])
    except:
        fullNodeServer.sendataspecfic()
    #ip = grabPublicIp()
"""
#end
