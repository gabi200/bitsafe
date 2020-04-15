# (c) gabi200 - All rights reserved

import sys
import os
import base64
import time
import platform
import random
import getpass
import pyperclip
from os import path
from collections import defaultdict
from shutil import copyfile
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

def genkey(salt):
	kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=default_backend()
	)
	key = base64.urlsafe_b64encode(kdf.derive(password)) # Can only use kdf once
	return key

def genpassword(length):
	letters = "abcdefghijklmnopqrstuvwxyz"
	password = ""
	# x and y are random numbers used for password generation
	for i in range(length):
		x = random.randint(0,100)
		y = random.randint(100, 500)
		index = random.randint(0, len(letters) - 1)
		index1 = random.randint(0, len(letters) - 1)

		password += str(x) + letters[index] + letters[index1] + str(y)
	return password

version = " v1.1.1"
bar = "=" * 65
password_dict = defaultdict(dict)
service_name = ""
index = 0
auth = False

if platform.system() == "Windows":
	keypath = "C:\\ProgramData\\BitSafe"
	os.system("title BitSafe Password Manager" + version)
elif platform.system() == "Linux":
	keypath = "/home/.bitsafe"
	sys.stdout.write("\x1b]2;BitSafe Password Manager" + version + "\x07")

def clear():
	if platform.system() == "Windows":
		os.system("cls")
	elif platform.system() == "Linux":
		os.system("clear")

clear()
print ("BitSafe Password Manager CLI" + version)
print("This is a simple, open-source, lightweight and secure password manager. Everything is being kept locally on your device.")
print(bar)
input("Press [enter] to continue.")


clear()

if path.exists(keypath + "\\installed.txt"):
	print("Welcome back!")
	password_provided = getpass.getpass("Please enter your password: ")
	new = False
else:
	if not path.exists(keypath):
		os.mkdir(keypath)
	print("You need to set a password. Warning: If you lose this password, all your stored passwords are lost forever!")
	print("Note: it is normal to not see your password while you're typing it.")

	password_provided = getpass.getpass("Please enter your password: ")
	password_check = getpass.getpass("Please repeat your password: ")

	if not password_provided == password_check:
		print("Password does not match! Please try again.")
		input("Press [enter] to continue.")
		sys.exit()
		
	file = open(keypath + "\\installed.txt","w")
	file.close()
	new = True

password = password_provided.encode() # Convert to type bytes
if new == True:
	salt = os.urandom(16)
	key = genkey(salt)

	file0 = open(keypath + "\\salt", 'wb')
	file0.write(salt)
	file0.close()

	f = Fernet(key)
	encrypted = f.encrypt("identity_check_9674".encode())

	file = open(keypath + "\\idcheck.key", 'wb')
	file.write(encrypted)
	file.close()

file = open(keypath + "\\salt", 'rb')
salt = file.read() 
file.close()

file = open(keypath + "\\idcheck.key", 'rb')
encrypted = file.read() 
file.close()

key_check = genkey(salt)
f = Fernet(key_check)

try:
	if f.decrypt(encrypted) == "identity_check_9674".encode():
		clear()
		print("Authentication sucessful!")
		time.sleep(3)
		clear()
		auth = True
except:
	print("Authentication failed!")
	time.sleep(3)
	sys.exit()
while True:
	if auth == True:
		clear()
		password_dict = defaultdict(dict)
		print("My Passwords")
		print("Commands: [add] [view] [delete] [reset] [backup] [generate] [exit]")
		print(bar)
		if not path.exists(keypath + "\\securedata.pwd"):
			file = open(keypath + "\\securedata.pwd","wb")
			file.write("default".encode())
			file.close()
		file = open(keypath + "\\securedata.pwd", "rb")
		data = file.read()
		file.close()

		if data == "default".encode():
			print("You don't have any passwords saved.")
			data_decoded = ""
		else:
			data_decoded = f.decrypt(data)
			for i in data_decoded.decode():
				if i != ";":
					if i != ":":
						if index == 0:
							service_name += i
						elif index == 1:
							if service_name in password_dict:
								password_dict[service_name] += i
							else:
								password_dict[service_name] = ""
					else:
						index += 1
				else:
					service_name = ""
					index = 0

		for i in password_dict:
			print(i)

		print(bar)
		command = input("Enter command: ")

		if command.lower() == "add":
			clear()
			print("Add password")
			print(bar)
			serv_name = input("Service name: ")
			pwd = getpass.getpass("Password: ")
			if data == "default".encode():
				data_decoded_2 = data_decoded
			else:
				data_decoded_2 = data_decoded.decode()
			data_decoded_2 += serv_name + ": " + pwd + ";"
			data_encrypted = f.encrypt(data_decoded_2.encode())

			file = open(keypath + "\\securedata.pwd", "wb")
			file.write(data_encrypted)
			file.close()

			print("Password added.")
			input("Press [enter] to continue.")
			clear()
		elif command.lower() == "view":
			show_pwd = False
			display = True
			clear()
			print("View entry details")
			print(bar)
			serv_name = input("Enter service name: ")
			while display == True:
				if not (data == "default".encode()) and (serv_name in password_dict):
					print(bar)
					if show_pwd == True:
						display = False
						print("Password for " + serv_name + ": " + password_dict[serv_name])
					elif show_pwd == False:
						print("Password for " + serv_name + ": ******")
						choice = input("Reveal password? (y/n): ")
						if choice.lower() == "y":
							show_pwd = True
					input("Press [enter] to continue.")
				else:
					print("Error: Service name not found or no passwords added.")
					input("Press [enter] to continue.")
					display = False
				clear()
		elif command.lower() == "reset":
			clear()
			print("Do you want to delete all the information from this app, including your passwords?")
			print("WARNING: this cannot be undone. You will lose all your passwords.")
			print(bar)
			choice = input("Type \"confirm\" to delete everything or leave empty to cancel: ")
			if choice == "confirm":
				print("Deleting...")
				time.sleep(1)

				os.remove(keypath + "\\salt")
				os.remove(keypath + "\\idcheck.key")
				os.remove(keypath + "\\securedata.pwd")
				os.remove(keypath + "\\installed.txt")

				password_dict = defaultdict(dict)
				service_name = ""
				index = 0
				auth = False

				print("Reset done.")
				input("Press [enter] to continue.")
				sys.exit()
			else:
				clear()
		elif command.lower() == "delete":
			clear()
			print("Delete entry")
			print(bar)
			serv_name = input("Service name: ")
			choice = input("Do you want to delete this password? (yes/no): ")
			if choice.lower() == "yes":
				print("Deleting...")
				try:
					data_to_delete = serv_name + ": " + password_dict[serv_name] + ";"
					if data == "default".encode():
						data_decoded_2 = data_decoded
					else:
						data_decoded_2 = data_decoded.decode()

					if data_to_delete in data_decoded_2:
						data_modified = data_decoded_2.replace(data_to_delete, "")

					encrypted = f.encrypt(data_modified.encode())

					file = open(keypath + "\\securedata.pwd", "wb")
					file.write(encrypted)
					file.close()
					print("Done!")
					input("Press [enter] to continue.")
					clear()
				except:
					print("Error: entry does not exist")
					input("Press [enter] to continue.")
					clear()
		elif command.lower() == "backup":
			clear()
			print("Backup")
			print(bar)
			print("You can use this feature to export your passwords to another device or import them from another device.")
			choice = input("Select \"import\" or \"export\": ")

			if choice.lower() == "export":
				disk_letter = input("Please enter disk letter where to export: ")
				print("Exporting...")
				exportpath = disk_letter.upper() + ":\\BitSafe"

				if not path.exists(exportpath):
					os.mkdir(exportpath)

				copyfile(keypath + "\\salt", exportpath + "\\salt")
				copyfile(keypath + "\\idcheck.key", exportpath + "\\idcheck.key")
				copyfile(keypath + "\\securedata.pwd", exportpath + "\\securedata.pwd")

				print("Done! You can now import the backup on another device!")
				input("Press [enter] to continue.")
				clear()
			elif choice.lower() == "import":
				disk_letter = input("Please enter disk letter where the backup is located: ")
				importpath = disk_letter.upper() + ":\\BitSafe"

				if path.exists(importpath):
					print("Importing...")
					copyfile(importpath + "\\salt", keypath + "\\salt")
					copyfile(importpath + "\\idcheck.key", keypath + "\\idcheck.key")
					copyfile(importpath + "\\securedata.pwd", keypath + "\\securedata.pwd")

					print("Done!")
					input("Press [enter] to continue.")
					sys.exit()
				else:
					print("Error: path does not exist!")
					input("Press [enter] to continue.")
					clear()
		elif command.lower() == "generate":
				clear()
				print("Generate password")
				print(bar)
				length = input("Enter length (note: it isn't the number of characters, enter any integer): ")
				password = genpassword(int(length))
				print(bar)
				print("Your password is: " + password)
				choice = input("Do you want to copy it to clipboard? (y/n): ")

				if choice.lower() == "y":
					pyperclip.copy(password)
					print("Password copied.")
				
				input("Press [enter] to continue.")
				clear()
		elif command.lower() == "exit":
			sys.exit()
		else:
			print("Error: invalid command")
			input("Press [enter] to continue.")
			clear()