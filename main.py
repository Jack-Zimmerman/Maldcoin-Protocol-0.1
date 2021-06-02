#text encoding is in ISO-8859-1

#grabbing blockchain external functions:
from blockchainFunctions import *
from blockchainFunctions import stringHash
from blockchainFunctions import rawHash
from blockchainFunctions import addHash
from blockchainFunctions import arbDifficulty
from blockchainFunctions import verifyBlock
from blockchainFunctions import verifyTransaction
from blockchainFunctions import nodeVerifyTransaction
from blockchainFunctions import mine

#grabbing blockchain external classes 
from blockchainFunctions import blockChain
from blockchainFunctions import inputPassword
from blockchainFunctions import wallet
from blockchainFunctions import blockChain
from blockchainFunctions import transaction
from blockchainFunctions import block 

#pip libraries
import hashlib 
from merklelib import MerkleTree

import time
import os
import random
import json
import ecdsa
import codecs
import cryptocode
import zlib, base64
import socket

from fullnode import writeKnownData
from fullnode import nodeCommand



password = input("password for wallet: ")
inputPassword(password)

wallet1 = wallet()
wallet1.publicHex = wallet1.retrievePublic()


blockchain = blockChain()
blockchain.createGenesis(wallet1)



for x in range(1):
    block1 = block(blockchain)

    block1.addTransaction(blockchain, wallet1.simpleTransaction(password, hex(random.getrandbits(256)), 1000000000))

    block1.complete(time.time())
    mine(block1, wallet1, blockchain)

blockchain.writeToFile()
