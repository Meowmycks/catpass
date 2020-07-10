#! /usr/bin/python3
# coding = latin-1

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from pathlib import Path #to use Linux/OS X's "touch" function on Windows
import json #to hold our passwords
import getpass #to hide user input for entering passwords
import string #to generate new passwords
import random #also to generate new passwords
import os #to do stuff on the user's operating system
import platform #to determine what operating system the user is using
import signal #to kill the program when the user is done (on Linux/OS X)
import time #to display messages before the screen updates
import collections #for an ordered dictionary to make sorting and finding easier


#padding system for bytestrings
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[0:-ord(s[-1])]

#makes clearing the screen easier
def clearscreen(myOS = platform.system()):
    #the user is using Linux or OS X
    if myOS == 'Linux' or myOS == 'Darwin':
        _=os.system("clear")
    #the user is using Windows
    else:
        _=os.system("cls")

#getting AES of passphrase
def getAES(passphrase):
    encoded = passphrase.encode()
    hashphrase = SHA256.new(data = encoded)
    digest = hashphrase.digest()
    key = digest[:16]
    IV = digest[16:]
    return AES.new(key,AES.MODE_CBC,IV)

#encrypting message with given passphrase
def encrypt(message, passphrase):
    obj = getAES(passphrase)
    padded = pad(message).encode("utf8")
    return obj.encrypt(padded)

#decrypting ciphertext with given passphrase
def decrypt(ciphertext,passphrase):
    obj = getAES(passphrase)
    message = obj.decrypt(ciphertext)
    message = unpad(message.decode())
    return message

#to generate passwords for accounts
#to prevent possible problems with strings, " and ' are removed from the list
punct = string.punctuation
punct = punct.replace("\"","")
punct = punct.replace("\'","")

def generator(size, chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + punct):
    return ''.join(random.choice(chars) for _ in range(int(size)))

#used to separate information into different variables or other things as needed
#there's probably a much better way of doing this but whatever, it works
def getinfo(thelist):
    info = ""
    for item in thelist:
        info = info + item + " "
    return info.split()

#the dictionary to hold accounts in
passwords = collections.OrderedDict()

#find the .json file holding encrypted passwords
directory = os.listdir(os.getcwd())

#check if it exists first
#if not, then we make a new one
if "passwords.json" not in directory and "passwords-backup.json" not in directory:
    #the user is using Linux or OS X
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        _=os.system('touch passwords.json')
        _=os.system('touch passwords-backup.json')
    #the user is using Windows
    else:
        Path('passwords.json').touch()
        Path('passwords-backup.json').touch()

#getting user input for passphrase creation/verification
clearscreen()
passphrase = getpass.getpass("Enter passphrase: ")

#using passphrase to decrypt passwords
#if given wrong passphrase, it will ask for the passphrase again
#three strikes and you're out
failcount = 0;
while True:
    try:
        data = open("passwords.json","rb")
        encrypted = data.read()
        data.close()
        if encrypted:
            plaintext = decrypt(encrypted,passphrase)
            data = open("passwords.json","w")
            passwords = json.loads(plaintext)
            data.close()
        else:
            data = open("passwords-backup.json","rb")
            encrypted = data.read()
            data.close()
            if encrypted:
                plaintext = decrypt(encrypted,passphrase)
                data = open("passwords.json","w")
                passwords = json.loads(plaintext)
                data.close()
        break
    except:
        failcount+=1
        if failcount == 3:
            print("\nError: Bad passphrase.")
            time.sleep(1)
            exit(1)
        print("\nSorry, try again.")
        passphrase = getpass.getpass("Enter passphrase: ")

#upon login (successful decryption), the user will be greeted
clearscreen()
print("catpass v2020.07.10")
print("An Arguably Competent Password Manager")
print("Made by Meowmycks\n")

#the main menu
while True:
    print("A to Add an Account")
    print("V to View an Account")
    print("C to Change an Account")
    print("R to Remove an Account")
    print("P to Change Passphrase")
    print("E to Exit")
    choice = input("\nEnter command: ")
    clearscreen()

    #the user wants to add a new password
    if choice.lower() == 'a':
        clearscreen()
        site = input("Enter sitename: ")
        user = input("Enter username: ")
        #to make sure they enter a valid number
        while True:
            try:
                size = int(input("Give a length for your password: "))
                break
            except ValueError:
                pass
        for pw in passwords:
            siteinfo = getinfo(passwords[pw])
        password = generator(size)
        passwords[password] = [password]
        passwords[password].append(site)
        passwords[password].append(user)
        info = getinfo(passwords[password])
        clearscreen()
        print("Account Added")
        print("User \'{}\' at \'{}\' has the password \'{}\'\n".format(info[2],info[1],info[0]))

    #the user wants to look at a password
    if choice.lower() == 'v':
        clearscreen()
        #if passwords exist then list all of them
        if len(passwords) != 0:
            print("List of Known Accounts\n")
            #we use position to list off each account, this will matter later
            position = 1
            for pw in passwords:
                info = getinfo(passwords[pw])
                print("{} | Site: {} | User: {}".format(position,info[1],info[2]))
                position += 1
            #to make sure they enter a valid number
            while True:
                try:
                    accno = int(input("\nChoose an Account Number: "))
                    break
                except ValueError:
                    pass
            #for when they choose a number outside the available list
            if accno > 0 and accno <= len(passwords):
                verify = getpass.getpass("\nEnter passphrase: ")
                clearscreen()
                #now that we know what account they want, we go back to that position
                #because we are using an ordered dictionary, our job is *much* easier
                position = 0
                if verify == passphrase:
                    for pw in passwords:
                        info = getinfo(passwords[pw])
                        position+=1
                        #give the account info at the given index
                        if position == accno:
                            print("User \'{}\' at \'{}\' has the password \'{}\'\n".format(info[2],info[1],info[0]))
                else:
                    print("Error: Bad passphrase.\n")
            else:
                clearscreen()
                print("No account exists at that index.\n")
        #for when no accounts exist
        else:
            print("No accounts saved.\n")
    
    #the user wants to change an existing password
    if choice.lower() == 'c':
        clearscreen()
        #you can't change a nonexistent password
        if len(passwords) != 0:
            #clearscreen()
            print("List of Known Accounts\n")
            #we use position to list off each account, this will matter later
            position = 1
            for pw in passwords:
                info = getinfo(passwords[pw])
                print("{} | Site: {} | User: {}".format(position,info[1],info[2]))
                position+=1
            #to make sure they enter a valid number
            while True:
                try:
                    accno = int(input("\nChoose an Account Number: "))
                    break
                except ValueError:
                    pass
            #for when they choose a number outside the available list
            if accno > 0 and accno <= len(passwords):
                verify = getpass.getpass("\nEnter passphrase: ")
                clearscreen()
                #now that we know what account they want, we go back to that position
                #because we are using an ordered dictionary, our job is *much* easier
                position = 0
                canchange = False
                if verify == passphrase:
                    for pw in passwords:
                        info = getinfo(passwords[pw])
                        #this holder will become very important later
                        holdpw = info[0]
                        position+=1
                        #change the account info at the given index
                        if position == accno:
                            #let the user choose what they want to change
                            #in all three cases, the user enters new information
                            #that information overwrites previous information stored in "info"
                            #which then overwrites the corresponding information in "pw"
                            #changing passwords is a bit more complicated
                            #instead of replacing one part, it deletes the key
                            #and adds a new key in the same spot with the new information
                            #there's probably a better way to do it but whatever, it works
                            clearscreen()
                            while True:
                                print("S to Change Site")
                                print("U to Change User")
                                print("P to Change Password")
                                print("E to Exit")
                                print("R does nothing.")
                                changeme = input("\nEnter command: ")
                                #change sitename
                                if changeme.lower() == 's':
                                    clearscreen()
                                    site = input("Enter sitename: ")
                                    info[1] = site
                                    passwords[pw] = info
                                    clearscreen()
                                    print("Site changed successfully.\n")
                                #change username
                                elif changeme.lower() == 'u':
                                    clearscreen()
                                    user = input("Enter username: ")
                                    info[2] = user
                                    passwords[pw] = info
                                    clearscreen()
                                    print("User changed successfully.\n")
                                #change password
                                elif changeme.lower() == 'p':
                                    clearscreen()
                                    while True:
                                        try:
                                            size = int(input("Give a length for your password: "))
                                            break
                                        except ValueError:
                                            pass
                                    password = generator(size)
                                    info[0] = password
                                    #password replacement has been enabled
                                    canchange = True
                                    clearscreen()
                                    print("Password changed successfully.\n")
                                #go back to main menu
                                elif changeme.lower() == 'e':
                                    clearscreen()
                                    break
                                elif changeme.lower() == 'r':
                                    clearscreen()
                                    print("I said it does nothing, stupid.\n")
                                    pass
                                else:
                                    clearscreen()
                                    pass
                
                else:
                    print("Error: Bad passphrase.\n")
                #if 
                if canchange:
                    #boom
                    del passwords[holdpw]
                    passwords[info[0]] = [info[0]]
                    passwords[info[0]].append(info[1])
                    passwords[info[0]].append(info[2])
            else:
                clearscreen()
                print("No account exists at that index.\n")
        else:
            print("No accounts saved.\n")
    
    #the user wants to change their decryption password
    if choice.lower() == 'p':
        clearscreen()
        #make sure the user knows their passphrase
        #if they do, then they can change it
        #to make sure they know what they're typing, make them do it twice
        #if everything checks out, their passphrase changes
        verify = getpass.getpass("Enter old passphrase: ")
        if passphrase == verify:
            newpass = getpass.getpass("Enter new passphrase: ")
            verifynewpass = getpass.getpass("Re-enter new passphrase: ")
            if newpass == verifynewpass:
                passphrase = newpass
                clearscreen()
                print("Passphrase updated.\n")
            else:
                clearscreen()
                print("Error: New passphrases do not match.\n")
        else:
            clearscreen()
            print("Error: Bad passphrase.\n")
    
    #the user wants to remove a password
    if choice.lower() == 'r':
        clearscreen()
        #you can't remove a nonexistent password
        if len(passwords) != 0:
            #clearscreen()
            print("List of Known Accounts\n")
            #we use position to list off each account, this will matter later
            position = 1
            for pw in passwords:
                info = getinfo(passwords[pw])
                print("{} | Site: {} | User: {}".format(position,info[1],info[2]))
                position+=1
            #to make sure they enter a valid number
            while True:
                try:
                    accno = int(input("\nChoose an Account Number: "))
                    break
                except ValueError:
                    pass
            #now that we know what account they want, we go back to that position
            #because we are using an ordered dictionary, our job is *much* easier
            position = 0
            if accno > 0 and accno <= len(passwords):
            #make sure it's the user doing it
                verify = getpass.getpass("\nEnter passphrase: ")
                clearscreen()
                if verify == passphrase:
                    for pw in passwords:
                        info = getinfo(passwords[pw])
                        #delete the account at the given index
                        if position == accno-1:
                            del passwords[info[0]]
                            clearscreen()
                            print("Account removed.\n")
                            break
                        else:
                            position+=1
                            pass
                else:
                    print("Error: Bad passphrase.\n")
            else:
                clearscreen()
                print("No account exists at that index.\n")
        else:
            print("No accounts saved.\n")
    
    #the user wants to close the program
    #when exiting the program, we encrypt and dump our passwords into the json file
    if choice.lower() == 'e':
        dump = json.dumps(passwords)
        encrypted = encrypt(dump,passphrase)
        data = open("passwords.json","wb")
        data.write(encrypted)
        data.close()
        data = open("passwords-backup.json","wb")
        data.write(encrypted)
        data.close()
        clearscreen()
        exit(1)