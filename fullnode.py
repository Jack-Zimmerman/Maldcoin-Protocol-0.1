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
from ConnectionFunctions import grabPrivateIp
from ConnectionFunctions import ClientConnection

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
            elif self.request.startswith("00000000000000000000000000000000CONNECTBACK00000000000000000000000000000000"):
                return self.connectBack()
        except Exception as e:
            return "INVALID_REQUEST" + str(e)

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
                self.node.server.sendataspecfic(
                    "00000000000000000000000000000000TRANSACTION00000000000000000000000000000000" + str(
                        grabbedTransaction), self.node.server.connections.values()[i][0])
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
                self.node.server.sendataspecfic(grabbedBlock, self.node.server.connections.values()[i][0])
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

    def connectBack(self):
        newClientSocket = ClientConnection(self.request[75:], 26527)
        self.node.server.clientConnections.append([newClientSocket, self.request[75:]])
        return



class FullNode():

    def __init__(self, hostingIPAdress):
        self.hostingIPAdress = hostingIPAdress
        self.server = Server(hostingIPAdress, 26527, 5)
        self.knownNodes = ["10.0.0.190"]

    def accecptConnections(self):

        # Defining the thread
        def acceptConnectionsThread():
            while True:
                self.server.acceptconnections()
                self.server.numCurrentConnections = len(self.server.connections)
                self.server.sendataspecfic(
                    "0000000000000000000000000000000" + str(self.knownNodes) + "0000000000000000000000000000000",
                    self.server.connections[self.server.numCurrentConnections - 1][0])

        # Threading the connection acceptor
        acceptingConnectionsThread = threading.Thread(target=acceptConnectionsThread)
        print("\n$Accepting Connections\n")
        acceptingConnectionsThread.start()

    def handleRequests(self):

        # Defining the thread
        def handleRequestsThread():
            while True:
                try:
                    for i in range(len(self.server.connections)):
                        self.server.recievemsg(self.server.connections[i][0])
                        if self.server.finalmsg != "":
                            print("$Recieved mesasge: " + str(self.server.finalmsg))
                        request = nodeCommand(self)
                        toReturn = request.handleRequest(self.server.finalmsg)
                        self.server.sendataspecfic(str(toReturn), self.server.connections[i][0])
                        print("$Returned: " + str(toReturn) + " to " + str(self.server.connections[i][1]) + "\n")
                except:
                    pass

        # Threading Handle Requests
        handleRequestsThread = threading.Thread(target=handleRequestsThread)
        print("$Proccesing Requests\n")
        handleRequestsThread.start()

    def startUp(self):

        for i in range(len(self.knownNodes)):
            try:
                newClientSocket = ClientConnection(self.knownNodes[i], 26527)
                self.server.clientConnections.append([newClientSocket, self.knownNodes[i]])
                print("$Connected to: " + str(self.knownNodes[i]) + "\n")
                try:
                    newNodes = list(newClientSocket.finalmsg[31:31])
                    for f in range(len(newNodes)):
                        if not (newNodes[f] in self.knownNodes):
                            self.knownNodes.append(newNodes[f])
                except Exception as e:
                    print("ERROR : " + str(e))
                    return
                print("$New nodes: " + str(self.knownNodes) + "\n")

            except Exception as e:
                print("$ERROR: CONNECTION TO " + str(self.knownNodes[i]) + " FAILED: " + str(e) + "\n")

        for j in range(len(self.server.clientConnections)):
            try:
                self.server.clientConnections[j][0].sendmsg(
                    "00000000000000000000000000000000CONNECTBACK00000000000000000000000000000000" + str(
                        self.hostingIPAdress))
                print("$Connect back asked of: " + str(self.server.clientConnections[j][1]))
                try:
                    self.server.recievemsg(self.server.connections[j][0])
                    if self.server.finalmsg == "CONFIRMED":
                        print("$CONFIRMED\n")
                except Exception as e:
                    print("$ERROR: CONNECT BACK FAILED: " + str(e) + "\n")
            except Exception as e:
                print("$ERROR: DATA SEND TO: " + str(self.server.clientConnections[j][0]) + " FAILED: " + str(e) + "\n")

        self.accecptConnections()
        self.handleRequests()



# Server Start:

fullNodeServer = FullNode("10.0.0.38")

fullNodeServer.startUp()



# end
