#text encoding is in ISO-8859-1

import hashlib 
from merklelib import MerkleTree

import time
import copy
import json
import ecdsa
import codecs
import cryptocode
import zlib, base64 

password = input("password for wallet: ")

block_reward = 50000000

def stringHash(string):
    return hashlib.sha256(str(string).encode('ISO-8859-1')).hexdigest()

def rawHash(string):
    return hashlib.sha256(str(string).encode()).digest()

def addHash(string1, string2):
    return stringHash(rawHash(string1) + rawHash(string2))    

def addHashRaw(string1, string2):
    return rawHash(rawHash(string1) + rawHash(string2))

def arbDifficulty(hashDemand):
    highest = bin((2**256)-1)
    hashDemand = int(hashDemand, 16)
    
    return bin(round((int(highest, 2))/hashDemand))

def verifyBlock(block):
    global block_reward

    if (addHash(rawHash(block["header"]), block["nonce"]) != block["proof"]):
        return False
    

    return True

def verifyTransactions(blockOld):
    block = copy.deepcopy(blockOld)

    block.transactions = [(x.__dict__) for x in block.transactions]

    block = block.__dict__

    for x in block["transactions"]:
        if (verifyTransaction(x) == False):
            del x
        
        if x["sender"] == "COINBASE":
            if x["txamount"] != block_reward:
                del x
            elif ((x["outputs"][0][1]) + (x["outputs"][1][1])) != block_reward:
                del x
        

def verifyTransaction(transaction):
    try:
        ecdsa.VerifyingKey.from_string(bytes.fromhex(transaction["sender"]),curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256).verify(bytes(transaction["signed"], "ISO-8859-1"), bytes(transaction["txhash"] + transaction["nonce"], "ISO-8859-1"))
    except:
        return False

    
def nodeVerifyTransaction(transaction):
    if (verifyTransaction(transaction)):
        transaction.verifications += 1


            
    


class blockChain:
    def __init__(self):
        self.blockchain = []
        self.chainDict = []
        self.size = len(self.chainDict)  
        self.dataSize = len(json.dumps(self.chainDict)) 

    def createGenesis(self, miner):
        genesis = block(self)
        genesis.difficulty = "{:012x}".format(2000)
        genesis.complete(time.time())
        mine(genesis, miner, self)

    def addBlock(self, block):
        self.blockchain.append(block)
        self.chainDict.append(block.__dict__)
        self.size = len(self.chainDict)

    def writeToFile(self):
        try:
            data = json.dumps(self.chainDict)
            data =  base64.b64encode(zlib.compress(data.encode('ISO-8859-1'),9)) 
            data = data.decode('ISO-8859-1')

            file = open("blockchain.dat", 'w')
            file.write(data)
            file.close()
            return True
        except:
            return False

    def retrieveFromFile(self):
        try:
            file = open("blockchain.dat", 'r')
            data = json.loads(codecs.decode(zlib.decompress(base64.b64decode(file.read())), "ISO-8859-1"))
            file.close()

            return data
        except:
            print("file not found!!")
            return self.chainDict

    def decompressFile(self):
        file = open("blockchain.dat", 'r')
        data = json.loads(codecs.decode(zlib.decompress(base64.b64decode(file.read())), "ISO-8859-1"))
        file.close()

        file = open("blockchaindecompressed.dat", 'w')
        file.write(json.dumps(data))
        file.close()

    def syncChain(self):
        self.chainDict = self.retrieveFromFile()
        blockchain.size = len(self.chainDict)
            


class block:
    def __init__(self, blockchain):
        self.height = blockchain.size

        if (self.height != 0):
            self.previousHash = blockchain.chainDict[-1]["proof"] 
        else:
            self.previousHash = "0"

        self.version = 0.1
        self.transactions = []
        self.difficulty = self.calculateDifficuty(blockchain)
        self.nonce = 0

    def calculateDifficuty(self, blockChain):
        chain = blockChain.chainDict
        if (self.height == 0): return 
        if (self.height % 144 == 0):
            total_time = round(time.time(), 2) - chain[self.height - 144]["timeStamp"]
            
            return "{:012x}".format(round(int(chain[self.height - 1]["difficulty"],16) * ((1440 * 60)/total_time)))
        else:
            return chain[self.height - 1]["difficulty"]
    
    def addTransaction(self, transaction):
        self.transactions.append(transaction)

    def complete(self, timestamp): 
        self.timeStamp = round(timestamp, 2)
        self.header = stringHash(json.dumps([(x.__dict__) for x in self.transactions]) + str(self.timeStamp))

    def addFees(self, miner, fee):
        for x in range(len(self.transactions)):
            self.transactions[x].addFee(miner, fee)

    def addBlockToChain(self, blockchain, nonce):
        self.nonce = nonce
        self.main_chain = True
        self.tx_num = len(self.transactions)

        #murkleTree = MerkleTree(self.transactions, stringHash)
        self.murkleString = (str(MerkleTree(self.transactions, stringHash))[12:-2])
        
        self.transactions = [(x.__dict__) for x in self.transactions]

        self.size = len(self.__dict__) * 8
        blockchain.addBlock(self)

class transaction:
    privKey = ""
    def __init__(self, sender, reciever, amount, timestamp, privkey, nonce):
        global privKey
        privKey = privkey
        self.timestamp = round(timestamp, 2)
        self.sender = sender
        self.outputs = [[reciever, amount]]
        self.txamount = amount
        self.txhash = stringHash(sender + reciever + str(self.timestamp))
        self.verifications = 0
        self.nonce = nonce 
        self.sign()
        
        
    def sign(self):
        global privKey
        self.signed = str(ecdsa.SigningKey.from_string(bytes.fromhex(privKey),curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256).sign(bytes(self.txhash + self.nonce, 'ISO-8859-1')), 'ISO-8859-1')

    def addFee(self, miner, fee):
        self.outputs[0] = [self.outputs[0][0], self.txamount - fee]
        self.outputs.append([miner, fee])
        
    


class wallet: 
    def __init__(self):
        self.publicHex = ""
        self.privateHex = ""

    def generateKeys(self, password):
        global public
        global private

        private = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        public = private.get_verifying_key()
        self.publicHex = public.to_string("compressed").hex()
        privateHexUsable = private.to_string().hex()
        self.privateHex = cryptocode.encrypt(private.to_string().hex(), password)
        self.nonce = str(0)
        self.created = round(time.time(), 2)

        file = open("wallet.dat", 'w')
        file.write(json.dumps(self.__dict__))
        file.close()

        self.privateHex = privateHexUsable
    
    def retrieveNonce(self):
        file = open("wallet.dat", 'r')
        wallet = json.loads(file.read())
        file.close()

        wallet["nonce"] = str(int(wallet["nonce"]) + 1)

        file = open("wallet.dat", 'w')
        file.write(json.dumps(wallet))
        file.close()

        return wallet["nonce"]

    def retrievePrivate(self):
        global password
        file = open("wallet.dat", 'r')
        wallet = json.loads(file.read())
        file.close()

        return cryptocode.decrypt(wallet["privateHex"], password)
        
    def retrievePublic(self):
        file = open("wallet.dat", 'r')
        wallet = json.loads(file.read())
        file.close()

        return wallet["publicHex"]

    def sign(self, message):
        privkey = ecdsa.SigningKey.from_string(bytes.fromhex(self.retrievePrivate()),curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
        
        return privkey.sign(message)

    def verify(self, message, intended):
        pubkey = ecdsa.VerifyingKey.from_string(bytes.fromhex(self.retrievePublic()),curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)

        return pubkey.verify(message, intended)



#non class functions
    

def mine(block, miner, blockchain):
    global difficulty 
    hash = rawHash(block.header)
    startTime = time.time()

    for a in range(2 ** 32):
        diff = arbDifficulty(block.difficulty)
        for x in range(2 ** 32):
            calculated = addHash(hash, x)
            
            if (int(calculated, 16) < int(diff, 2)):
                print("Found nonce: " + str(x + (a*(2**32))) + "; Alterations: " + str(a))
                print("Hash: " + calculated)
                
                try:
                    if (x != 0):
                        print("Efficiency: " + str(round(round(x + (a*(2**32)))/(time.time() - startTime))) + " hashes per second")
                        print("Luck: " + str(round(int(block.difficulty,16)/x, 2)))
                    else:
                        print("nonce is 0")
                except:
                    print("infinite luck")

                block.addTransaction(transaction("COINBASE", miner.publicHex, 50000000, round(time.time(), 2), miner.privateHex, miner.retrieveNonce()))
                block.addFees(miner.publicHex, len(block.transactions) * 1000)
                block.proof = calculated
                block.addBlockToChain(blockchain, x)
                return
        
        block.complete(block.timeStamp + 0.001)
        hash = rawHash(block.header)




wallet1 = wallet()
wallet1.generateKeys(password)

wallet2 = wallet()
wallet2.generateKeys(password)

blockchain = blockChain()
blockchain.createGenesis(wallet1)

for x in range(10):
    block1 = block(blockchain)

    block1.addTransaction(transaction(wallet2.publicHex, wallet1.publicHex, 50000000, round(time.time(), 2), wallet2.privateHex, wallet2.retrieveNonce()))

    verifyTransactions(block1)

    block1.complete(time.time())
    mine(block1, wallet1, blockchain)

blockchain.writeToFile()
blockchain.decompressFile()


