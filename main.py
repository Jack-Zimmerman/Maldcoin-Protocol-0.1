#text encoding is in ISO-8859-1

#grabbing external functions:
from blockchainFunctions import *
from blockchainFunctions import stringHash
from blockchainFunctions import rawHash
from blockchainFunctions import addHash
from blockchainFunctions import arbDifficulty
from blockchainFunctions import verifyBlock
from blockchainFunctions import verifyTransaction
from blockchainFunctions import nodeVerifyTransaction
from blockchainFunctions import mine

#grabbing external classes 
from blockchainFunctions import inputPassword
from blockchainFunctions import wallet
from blockchainFunctions import blockChain
from blockchainFunctions import transaction
from blockchainFunctions import block 

#pip libraries
import hashlib 
from merklelib import MerkleTree

import time
import json
import ecdsa
import codecs
import cryptocode
import zlib, base64

password = input("password for wallet: ")
inputPassword(password)

block_reward = 50000000000

##############################################################################
#Hash functions for varying usage

wallet1 = wallet()
wallet1.publicHex = wallet1.retrievePublic()


blockchain = blockChain()
blockchain.syncChain()

"""
for x in range(87):
    block1 = block(blockchain)
        
    block1.complete(time.time())
    mine(block1, wallet1, blockchain)
"""

block1 = block(blockchain)
block1.addTransaction(blockchain, wallet1.simpleTransaction(password, stringHash("lmao??????"), 550000000))
block1.complete(time.time())
mine(block1, wallet1, blockchain)

blockchain.writeToFile()
blockchain.decompressFile()
