import os
from datetime import datetime, timezone
import math
import json
import cryptocode
import pyperclip
import time


from blockchainFunctions import wallet
from blockchainFunctions import generateBalance
from blockchainFunctions import blockChain
from blockchainFunctions import compressAddress
from blockchainFunctions import decompressAddress
from blockchainFunctions import verifyTransaction
from blockchainFunctions import transaction

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ANCHOR,END
from tkinter import ttk
from tkinter import messagebox
import urllib



#Global Variables START
password = ""
wallet = wallet()
blockchain = blockChain()
#Global Variables END

#Syncing blockchain START
syncingWindow = tk.Tk()
syncingWindow.title("Syncing Blockchain")
syncingWindow.geometry("300x200")
syncingWindow.resizable(False, False)

syncingLabel = tk.Label(syncingWindow, text="Syncing blockchain\nSize: " + str(round(os.stat(
    'blockchain.dat').st_size / 1000000000, 4)) + " GB\n\n" + "Sync time(s): " + str(math.ceil((os.stat(
    'blockchain.dat').st_size / 1000000) * 0.1)), width=20, font=("Courier", 20))
syncingLabel.place(relx=0.5,rely=0.4,anchor='center')
syncingLabel.update()

#chain sync protocol
blockchain.syncChain()
syncingWindow.destroy()
#Syncing blockchain END





#main window config START
main = tk.Tk()
main.title("Maldcoin Core 0.1")
main.geometry("600x400")
main.resizable(False, False)

mainMenu = tk.Menu(main)
filemenu = tk.Menu(mainMenu, tearoff=0)
filemenu.add_command(label="Run Node")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=lambda:quit())
mainMenu.add_cascade(label="File", menu=filemenu)
main.config(menu=mainMenu)
#main window config END

#Password entry mechanism START
enterPassword = tk.Tk()
enterPassword.title("Password")
enterPassword.geometry("200x100")
enterPassword.resizable(False, False)
enterPassword.lift()

#prompt changes depending on whether account is new or not
if os.path.isfile("wallet.dat"):
    prompt = "Enter Password: "
else:
    prompt = "Enter Password for new wallet: "

passwordPrompt = tk.Label(enterPassword, text=prompt)
passwordPrompt.place(relx=0.5, rely=0.15, anchor='center')

passwordEntry = tk.Entry(enterPassword, width=30)
passwordEntry.place(relx=0.5, rely=0.5, anchor='center')

passwordConfirm = tk.Button(enterPassword, width=20, text="login", command=lambda: login(passwordEntry.get()))
passwordConfirm.place(relx=0.5,rely=0.8,anchor='center')

enterPassword.eval(f'tk::PlaceWindow {str(enterPassword)} center')
#Password entry mechanism END


#Client information render START
style = ttk.Style()
current_theme =style.theme_use()
style.theme_settings(current_theme, {"TNotebook.Tab": {"configure": {"padding": [20, 5]}}})

tabControl = ttk.Notebook(main,height=400,width=600)
account = ttk.Frame(tabControl)
send = ttk.Frame(tabControl)
contacts = ttk.Frame(tabControl)
tabControl.add(account, text='Account')
tabControl.add(contacts, text='Contacts')
tabControl.grid(row=1, column=0, sticky=tk.NSEW)

#shows balance
balanceDescript = tk.Label(account,text="BALANCE:", width=20,height=2, font=("Bold", 25))
balanceDescript.place(relx=0.2, rely=0.3, anchor='center')

balanceLabel = tk.Label(account,text="0.000000000", width=20,height=2, font=("Roboto", 20))
balanceLabel.place(relx=0.65, rely=0.3, anchor='center')

#separates different pairs of elements
separator1 = ttk.Separator(account,orient='horizontal')
separator1.place(relx=0, rely=0.2, relwidth=1, relheight=0.000001)

separator2 = ttk.Separator(account,orient='horizontal')
separator2.place(relx=0, rely=0.4, relwidth=1, relheight=0.000001)

accountLabel = tk.Label(account,text="", height=2, font=("Roboto", 7))
accountLabel.place(relx=0.25, rely=0.08, anchor='center')

#render of current transaction list

txBox = tk.Listbox(account, width=95,relief="groove")
txBox.place(relx=0.5, rely=0.7,anchor='center')

#render of contacts list
contactsBox = tk.Listbox(contacts, width=95, height=15,relief="groove")
contactsBox.place(relx=0.5, rely=0.6, anchor='center')








#Client information render END

def login(temp):
    global password
    global wallet
    global blockchain
    global balanceLabel
    global accountLabel
    global passwordEntry
    global enterPassword
    global txBox

    password = temp

    if os.path.isfile("wallet.dat"):
        with open("wallet.dat", "r") as walletFile:
            walletDict = json.loads(walletFile.read())

            try:
                if (cryptocode.decrypt(walletDict["privateHex"], password) == False):
                    messagebox.showwarning("PASSWORD ERROR[1]", "Incorrect Password")
                else:
                    wallet.private = cryptocode.decrypt(walletDict["privateHex"], password)
                    enterPassword.destroy()
            except:
                pass

            wallet.public = walletDict["publicHex"]
            balanceLabel.config(text=str(round(generateBalance(blockchain, wallet.public)/1000000000, 9)) + " MDC")
            accountLabel.config(text="Account: " + str(compressAddress(wallet.public)),background="white")

            copyAddress = tk.Button(account, text="copy", command=lambda: pyperclip.copy(compressAddress(wallet.public)),width=6,height=1, font=("Roboto", 8))
            copyAddress.place(relx=0.53, rely=0.08, anchor='center')

            localAddress = wallet.retrievePublic()

            #update transaction list when logged in START
            totalInserted = 0
            for x in blockchain.chainDict:
                for y in x["transactions"]:
                    if y["sender"] == localAddress:
                        for output in y["outputs"]:
                            try:
                                address = compressAddress(output[0])
                            except:
                                try:
                                    address = compressAddress(output[0][2:])
                                except:
                                    address = "UNKNOWN"

                            txBox.insert(END,f"{output[1] / 1000000000} MDC to {address}" + " | (" + datetime.utcfromtimestamp(y["timestamp"]).replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%Y-%m-%d %H:%M:%S') + ")")
                            txBox.insert(END, [("-") for x in range(95)])
                    else:
                        for output in y["outputs"]:
                            if output[0] == localAddress:
                                if y["sender"] == "0000000000000000000000000000000000000000000000000000000000000000":
                                    sender = "Mining Block Reward"
                                else:
                                    sender = compressAddress(y["sender"])
                                txBox.insert(END,f"{output[1] / 1000000000} MDC from {sender}" + " | (" + datetime.utcfromtimestamp(y["timestamp"]).replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%Y-%m-%d %H:%M:%S') + ")")
                                txBox.insert(END, [("-") for x in range(95)])

                    main.update()
            #update transaction list when logged in END

            #Rendering rest of wallet
            renderSend()
            renderContacts()
    else:
        wallet.generateKeys(password)
        enterPassword.destroy()

        with open("wallet.dat", "r") as wallet:
            walletDict = json.loads(wallet.read())

            wallet.public = walletDict["publicHex"]
            balanceLabel.config(text=str(round(generateBalance(blockchain, wallet.public)/1000000000, 9)) + " MDC")
            accountLabel.config(text="Account: " + str(compressAddress(wallet.public)),background="white")

            copyAddress = tk.Button(account, text="copy", command=lambda: pyperclip.copy(compressAddress(wallet.public)),width=10,height=2, font=("Roboto", 12))
            copyAddress.place(relx=0.9, rely=0.4, anchor='center')


def renderSend():
    global account
    global wallet
    global password
    global blockchain

    def newTransactionWindow():
        txWin = tk.Tk()
        txWin.title("New Transaction")
        txWin.geometry("400x250")
        txWin.resizable(False, False)

        #tx variables:
        global outputs
        global blockchain
        global totalAmount
        global totalFee
        global wallet
        global txAmountLabel
        global txFeeLabel
        global currentTx
        global password
        outputs = []

        #mechanism for grabbing new output
        def newOutput():
            global outputs
            global wallet

            global txAmountLabel
            global txFeeLabel
            global password
            global currentTx
            currentTx = {}

            newOut = tk.Tk()
            newOut.title("New Output")
            newOut.geometry("400x100")
            newOut.resizable(False,False)

            recieverLabel = tk.Label(newOut, text="Reciever: ", font=("Arial", 10))
            recieverLabel.place(relx=0.13, rely=0.2, anchor='center')

            reciverInput = tk.Entry(newOut, width=50)
            reciverInput.place(relx=0.6, rely=0.2,anchor='center')

            amountLabel = tk.Label(newOut, text="Amount: ", font=("Arial", 10))
            amountLabel.place(relx=0.13, rely=0.45, anchor='center')

            amountInput = tk.Entry(newOut, width=15)
            amountInput.place(relx=0.335, rely=0.45, anchor='center')

            def addOutputFunc(newOut, reciever, amount):
                global outputs
                global password
                global currentTx
                newOut.destroy()

                outputs.append([reciever, int(float(amount) * 1000000000)])

                with open("wallet.dat","r") as wallet:
                    data = json.loads(wallet.read())
                    public = data["publicHex"]
                    private = cryptocode.decrypt(data["privateHex"], password)

                    #reading and updating nonce
                    nonce = data["nonce"]

                with open("wallet.dat", "w") as walletWrite:
                    data["nonce"] += 1
                    walletWrite.write(json.dumps(data))

                currentTx = transaction(public, reciever, int(float(amount) * 1000000000), time.time(), private,nonce)

                for x in outputs:
                    if not x in currentTx.outputs:
                        currentTx.addOutput(x)

                txAmountLabel.config(text="Total(+Fee): " + str(round((len(json.dumps(currentTx.__dict__)) ** 2 + currentTx.txamount)/1000000000,9)))
                txFeeLabel.config(text="Estimated Fee: " + str(round((len(json.dumps(currentTx.__dict__)) ** 2)/1000000000,9)))



                #estimating fee:

            addOutput = tk.Button(newOut, width=15, text="Add Output", font=("Arial", 10),background="blue",foreground="white",command=lambda:addOutputFunc(newOut, decompressAddress(reciverInput.get()), amountInput.get()))
            addOutput.place(relx=0.5, rely=0.8, anchor = 'center')

        #tx stats
        txAmountLabel = tk.Label(txWin, text="Total(+Fee): 0.000000000", font =("Arial",20))
        txAmountLabel.place(relx=0.5, rely=0.1,anchor='center')

        txFeeLabel = tk.Label(txWin, text="Estimated Fee: 0.000000000", font=("Arial", 20))
        txFeeLabel.place(relx=0.5, rely=0.3, anchor='center')
        #interact with tx
        newOutputButton = tk.Button(txWin, text="New Output",width=20, font=("Arial", 18), background="black", foreground="white", command=newOutput)
        newOutputButton.place(relx=0.5,rely=0.5,anchor='center')

        #for confirmTxButton -> verifies transaction

        def txValidCheck(rawTx):
            global blockchain

            if verifyTransaction(blockchain, rawTx):
                tk.messagebox.showinfo("Transaction Valid", "Transaction has been submitted,\nwaiting for confirmation...")
            else:
                tk.messagebox.showwarning("Transaction Invalid", "Transaction is invalid")


        confirmTxButton = tk.Button(txWin, text="Confirm and Send", width=22, font=("Bold", 20), background="blue",foreground="white", command=lambda:txValidCheck(currentTx))
        confirmTxButton.place(relx=0.5, rely=0.8, anchor='center')


    newTransaction = tk.Button(account, text="Send Coins ➔", width=15,font=("Bold", 15), background="green", foreground="white",command=newTransactionWindow)
    newTransaction.place(relx=0.8, rely=0.08, anchor='center')

def renderContacts(new={}):
    global contacts
    global contactsBox

    def addContact():
        global contactsBox
        contactEntry = tk.Tk()
        contactEntry.title("Add Contact")
        contactEntry.geometry("320x100")
        contactEntry.resizable(False, False)

        addrEntry = tk.Entry(contactEntry, width=50)
        addrEntry.place(relx=0.5, rely=0.2, anchor='center')
        addrEntry.insert(END, "Address")

        noteEntry = tk.Entry(contactEntry, width=50)
        noteEntry.place(relx=0.5, rely=0.4, anchor='center')
        noteEntry.insert(END, "Note")

        def insertToContacts(new):
            global contactsBox

            if (new["note"] == "Note"):
                new["note"] = ""

            contactsBox.insert(END, new["address"] + "  |  " + new["note"])

            with open("data/contacts.dat", "r") as contactsFlR:
                try:
                    contacts = json.loads(contactsFlR.read())
                except:
                    contacts = []
                contacts.append({"address" : addrEntry.get(), "note" : noteEntry.get()})

                with open("data/contacts.dat", "w") as contactsFl:
                    contactsFl.write(json.dumps(contacts))



        addContactFinal = tk.Button(contactEntry, width=30, background="blue", foreground="white", text="Add Contact to List", command=lambda:insertToContacts({"address" : addrEntry.get(), "note" : noteEntry.get()}))
        addContactFinal.place(relx = 0.5, rely=0.7, anchor='center')

    addContactButton = tk.Button(contacts, text="Add Contact", width=15, background="yellow", font=("Arial", 24), command=lambda:addContact())
    addContactButton.place(relx=0.25, rely=0.15, anchor='center')

    def copyContact():
        selected = contactsBox.get(ANCHOR)
        selected = selected.split("|")[0].replace(" ", "")
        pyperclip.copy(selected)

    copyContactButton = tk.Button(contacts, text="Copy Selected", width=15, background="green",foreground ="white", font=("Arial", 24),command=lambda: copyContact())
    copyContactButton.place(relx=0.75, rely=0.15, anchor='center')


    if os.path.isfile("data/contacts.dat"):
        try:
            with open("data/contacts.dat", "r") as contactsFile:
                contacts = json.loads(contactsFile.read())

                for x in contacts:
                    contactsBox.insert(END, x["address"] + " | " + x["note"])
        except:
            print("Contacts file either do not exist or file is in incorrect format [Warning]")
    else:
        print("Contacts file does not exist, not contacts remembered.")

        contactsFile = open("data/contacts.dat", "w")
        contactsFile.write("[]")
        contactsFile.close()



    #mainloops
main.mainloop()
