import os
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

from PIL import Image, ImageTk
import tkinter as tk
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

syncingLabel = tk.Label(syncingWindow, text="Syncing blockchain\nSize: " + str(round(os.stat('blockchain.dat').st_size/1000000000,4)) + " GB\n\n" + "Sync time(s): " + str(math.ceil((os.stat('blockchain.dat').st_size/1000000) * 0.1)), width=20,font=("Courier", 20))
syncingLabel.grid()
syncingLabel.place(relx=0.5,rely=0.4,anchor='center')
syncingLabel.update()

#chain sync protocol 
blockchain.syncChain()
syncingWindow.destroy()
#Syncing blockchain END





#main window config START
main = tk.Tk()
main.title("ShitCoin Core 0.1")
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
passwordPrompt.grid()
passwordPrompt.place(relx=0.5, rely=0.15, anchor='center')

passwordEntry = tk.Entry(enterPassword, width=30)
passwordEntry.grid()
passwordEntry.place(relx=0.5, rely=0.5, anchor='center')

passwordConfirm = tk.Button(enterPassword, width=20, text="login", command=lambda: login(passwordEntry.get()))
passwordConfirm.grid()
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
tabControl.add(send, text='Send')
tabControl.add(contacts, text='Contacts')
tabControl.grid(row=1, column=0, sticky=tk.NSEW)


balanceDescript = tk.Label(account,text="BALANCE:", width=20,height=2, font=("Bold", 25))
balanceDescript.grid()
balanceDescript.place(relx=0.2, rely=0.2, anchor='center')
balanceLabel = tk.Label(account,text="0.000000000", width=20,height=2, font=("Roboto", 20))
balanceLabel.grid()
balanceLabel.place(relx=0.65, rely=0.2, anchor='center')

accountLabel = tk.Label(account,text="", height=2, font=("Roboto", 12))
accountLabel.grid()
accountLabel.place(relx=0.43, rely=0.4, anchor='center')

#Client information render END

def login(temp):
    global password
    global wallet
    global blockchain
    global balanceLabel
    global accountLabel
    global passwordEntry
    global enterPassword

    password = temp

    if os.path.isfile("wallet.dat"):
        with open("wallet.dat", "r") as wallet:
            walletDict = json.loads(wallet.read())

            try:
                if (cryptocode.decrypt(walletDict["privateHex"], password) == False):
                    messagebox.showwarning("PASSWORD ERROR[1]", "Incorrect Password")
                else:
                    wallet.private = cryptocode.decrypt(walletDict["privateHex"], password)
                    enterPassword.destroy()
            except:
                pass

            wallet.public = walletDict["publicHex"]
            balanceLabel.config(text=str(round(generateBalance(blockchain, wallet.public)/1000000000, 9)) + " SHT")
            accountLabel.config(text="Account: " + str(compressAddress(wallet.public)),background="white")

            copyAddress = tk.Button(account, text="copy", command=lambda: pyperclip.copy(compressAddress(wallet.public)),width=10,height=2, font=("Roboto", 12))
            copyAddress.grid()
            copyAddress.place(relx=0.9, rely=0.4, anchor='center')

            #Rendering rest of wallet START
            renderSend()
            #Rendring rest of wallet END
    else:
        wallet.generateKeys(password)
        enterPassword.destroy()

        with open("wallet.dat", "r") as wallet:
            walletDict = json.loads(wallet.read())

            wallet.public = walletDict["publicHex"]
            balanceLabel.config(text=str(round(generateBalance(blockchain, wallet.public)/1000000000, 9)) + " SHT")
            accountLabel.config(text="Account: " + str(compressAddress(wallet.public)),background="white")

            copyAddress = tk.Button(account, text="copy", command=lambda: pyperclip.copy(compressAddress(wallet.public)),width=10,height=2, font=("Roboto", 12))
            copyAddress.grid()
            copyAddress.place(relx=0.9, rely=0.4, anchor='center')

def renderSend():
    global send

    def newTransactionWindow():
        #tx variables:
        global outputs
        outputs = []

        def newOutput():
            global outputs
            newOut = tk.Tk()
            newOut.title("New Output")
            newOut.geometry("400x100")
            newOut.resizable(False,False)

            recieverLabel = tk.Label(newOut, text="Reciever: ", font=("Arial", 10))
            recieverLabel.grid()
            recieverLabel.place(relx=0.13, rely=0.2, anchor='center')

            reciverInput = tk.Entry(newOut, width=50)
            reciverInput.grid()
            reciverInput.place(relx=0.6, rely=0.2,anchor='center')

            amountLabel = tk.Label(newOut, text="Amount: ", font=("Arial", 10))
            amountLabel.grid()
            amountLabel.place(relx=0.13, rely=0.45, anchor='center')

            amountInput = tk.Entry(newOut, width=15)
            amountInput.grid()
            amountInput.place(relx=0.335, rely=0.45, anchor='center')

            def addOutputFunc(newOut, reciever, amount):
                global outputs

                reciver = decompressAddress(reciever)
                amount = float(amount)
                outputs.append([reciver, amount])

                newOut.destroy()

            addOutput = tk.Button(newOut, width=15, text="Add Output", font=("Arial", 10),command=lambda:addOutputFunc(newOut, reciverInput.get(), amountInput.get()))
            addOutput.grid()
            addOutput.place(relx=0.5, rely=0.8, anchor = 'center')

        txWin = tk.Tk()
        txWin.title("New Transaction")
        txWin.geometry("400x300")
        txWin.resizable(False, False)

        newOutputLabel = tk.Button(txWin, text="New Output", font=("Arial", 15), command=newOutput)
        newOutputLabel.grid()
        newOutputLabel.place(relx=0.2,rely=0.1,anchor='center')


    sendMat = tk.Label(send, text="Send Shitcoins", font=("Bold", 25))
    sendMat.grid()
    sendMat.place(relx=0.3, rely=0.1,anchor='center')

    newTransaction = tk.Button(send, text="New Transaction", width=15,font=("Bold", 15), command=newTransactionWindow)
    newTransaction.grid()
    newTransaction.place(relx=0.7, rely=0.1, anchor='center')








    #mainloops
main.mainloop()
