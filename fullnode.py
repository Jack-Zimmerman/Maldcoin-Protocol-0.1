#text encoding is in ISO-8859-1

#pip libraries
import hashlib 
import merklelib 

import time
import json
import ecdsa
import codecs
import cryptocode
import zlib, base64
import socket

#grabbing blockchain external functions:
from blockchainFunctions import stringHash
from blockchainFunctions import rawHash
from blockchainFunctions import addHash
from blockchainFunctions import arbDifficulty
from blockchainFunctions import verifyBlock
from blockchainFunctions import verifyTransaction
from blockchainFunctions import nodeVerifyTransaction
from blockchainFunctions import generateBalance
from blockchainFunctions import mine

#grabbing blockchain external classes:
from blockchainFunctions import inputPassword
from blockchainFunctions import wallet
from blockchainFunctions import blockChain
from blockchainFunctions import transaction
from blockchainFunctions import block 

#grabbing network protocol external functions:
from ConnectionFunctions import fullmsg

#grabbing network protocol external classes:
from ConnectionFunctions import ClientConnection
from ConnectionFunctions import Server

blockchain = blockChain()
blockchain.syncChain()

pendingTransactions = []




def writeKnownData():
    global blockchain
    knownAccounts = []

    for x in blockchain.chainDict:
        for y in x["transactions"]:
            for z in y["outputs"]:
                if z[0] not in knownAccounts:
                    knownAccounts.append(z[0])

    data = {"bals" : {}}

    for account in knownAccounts:
        data["bals"][account] = generateBalance(blockchain, account)

    with open("knownData.dat", "w") as knownFile:
        knownFile.write(json.dumps(data))



class handleRequest:
    def __init__(self, request):
        self.request = request

    def updateRequest(self, new):
        self.request = new

    def handleRequest(self):
        try:
            if self.request.startswith("00000000000000000000000000000000GETCHAINDATA00000000000000000000000000000000"):
                return self.getchaindata()
            elif self.request.startswith("00000000000000000000000000000000TRANSACTION00000000000000000000000000000000"):
                return self.recieveTransaction()
            elif self.request.startswith("00000000000000000000000000000000BALANCE00000000000000000000000000000000"):
                return self.returnBalance()
            elif self.request.startswith("00000000000000000000000000000000BLOCK00000000000000000000000000000000"):
                return self.addBlock()
        except:
            return "INVALID_REQUEST"

    def getchaindata(self):
        global blockchain 

        request = json.loads(self.request.replace("00000000000000000000000000000000GETCHAINDATA00000000000000000000000000000000", ""))

        return blockchain.chainDict[request[0]: request[1]]
        #returns blockchain data from block of height index1 to block of height index2
                    
    
    def recieveTransaction(self):
        global blockchain
        grabbedTransaction = json.loads(self.request.replace("00000000000000000000000000000000TRANSACTION00000000000000000000000000000000", ""))


        if verifyTransaction(blockchain, grabbedTransaction):
            pendingTransactions.append(grabbedTransaction)
            return "ACCEPTED" + grabbedTransaction["txhash"]
        else:
            return "DECLINED" + grabbedTransaction["txhash"]

    def returnBalance(self):
        global blockchain

        account = self.request.replace("00000000000000000000000000000000BALANCE00000000000000000000000000000000", "")

        return generateBalance(blockchain, account)

    def addBlock(self):
        global blockchain

        grabbedBlock = json.loads(self.request.replace("00000000000000000000000000000000BLOCK00000000000000000000000000000000", ""))

        if verifyBlock(grabbedBlock):
            #add block to chain and disperse
            return "ACCEPTED" + grabbedBlock["header"]
        else:
            return "DECLINED" + grabbedBlock["header"]


#Server Start:
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
fullNodeServer = Server(local_ip, 1234, 10)



#x = handleRequest("00000000000000000000000000000000TRANSACTION00000000000000000000000000000000" + json.dumps(blockchain.chainDict[10]["transactions"][0]))