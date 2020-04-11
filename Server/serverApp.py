import PySimpleGUI as sg
import socket
import sys
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import time
from _thread import *
import threading

# Create server socket
srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [  [sg.Text('Welcome to the privateshare server!', size=(30, 1), font=("Helvetica", 25), text_color='gray')],
            [sg.Text('Server runs for 5 minutes at a time unless in current operation')],
            [sg.Text('Please note that the GUI will appear unresponsive during operations')],
            [sg.Text('Please enter the Port Number you wish to bind to:', size=(40, None)), sg.InputText()],
            [sg.Text('Please enter the Password of the Server:', size=(40, None)), sg.InputText()],
            [sg.Button('Run Server'), sg.Button('Close Server')] ]

# Create the Window
window = sg.Window('privateshare server', layout)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if values[0] and values[1]:
        port_number = int(values[0])
        server_password = values[1]
        if event in ('Run Server'):
            """ 
            Enclose the following two lines in a try-except block to catch
            exceptions related to already bound ports, invalid/missing
            command-line arguments, port number out of range, etc.
            """
            try:
                """
                Register the socket with the OS kernel so that commands sent
                to the user-defined port number are delivered to this program.
                """
                srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                srv_sock.bind(("0.0.0.0", int(port_number)))

                # Report success post-binding
                print("Server up and running: 0.0.0.0 " + str(port_number) + " Port")
                print("Waiting for connection")

                # Initialize connection queue
                srv_sock.listen(5)
            except Exception as e:
                # Print the exception message
                print(e)
                # Close the server socket as well to release its resources back to the OS
                srv_sock.close()

            running = True

            while running:
                # First generate a cryptographic key for server session from provided password
                # This key is used for encrypting data to be sent server side and decrypting data
                # received on the client side.
                password_provided = str(server_password)
                password = password_provided.encode() # Convert to type bytes
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                    backend=default_backend()
                )
                key = base64.urlsafe_b64encode(kdf.derive(password)) # Can only use kdf once
                """
                Surround the following code in a try-except block to account for
                socket errors as well as errors related to user input.
                """
                try:
                    """
                    Dequeue a connection request from the queue created by listen() earlier.
                    If no such request is in the queue yet, this will block until one comes
                    in. Returns a new socket to use to communicate with the connected client
                    plus the client-side socket's address (IP and port number).
                    """
                    cli_sock,cli_adr = srv_sock.accept()
                    print("Connected with" + str(cli_adr))

                    # Receive the initial request from client
                    request = cli_sock.recv(32)
                    commands = request.decode('utf-8').split(',')

                    # Handling of put request, sever side
                    if (commands[0] == "put"):
                        print("Put request received")
                        directory = os.listdir()
                        # Make sure the client entered the correct password before distributing key to client
                        if(commands[2] == password_provided):
                            cli_sock.send("---+".encode('utf-8'))
                            cli_sock.send(key)
                            print("They cryptographic key for this request has successfully been distributed")
                            
                            # Make sure the file is not a reupload, if yes then notify the client to continue
                            if(not commands[1] in directory):
                                cli_sock.send("---+".encode('utf-8'))

                                # Try opening the file with exclusive creation binary mode
                                try:
                                    f = open(commands[1],'xb')
                                except FileExistsError:
                                    print("This file already exists")
                                data = cli_sock.recv(33554432)
                                collection = data
                                # Begin receiving the upload
                                while(data):
                                    print("Receiving...")
                                    data = cli_sock.recv(33554432)
                                    collection += data
                                fe = Fernet(key)
                                decrypted = fe.decrypt(collection)
                                f.write(decrypted)
                                f.close()
                                print("Done Receiving!!!")
                                cli_sock.close()
                        
                            # If file is a reupload, notify the client and reject the file
                            else:
                                cli_sock.send("----".encode('utf-8'))
                                time.sleep(1)
                                print("The server rejected the file. Filename already taken")
                                cli_sock.close()
                        else:
                            cli_sock.send("----".encode('utf-8'))
                            cli_sock.close()

                    # Handling of get request, server side
                    elif(commands[0] == "get"):
                        print("Get request received")
                        directory = os.listdir()

                        # Make sure the client entered the correct password before distributing key to client
                        if(commands[2] == password_provided):
                            cli_sock.send("---+".encode('utf-8'))
                            cli_sock.send(key)
                            print("They cryptographic key for this request has successfully been distributed")

                            # Make sure the file is in the servers directory, if yes then continue accordingly
                            if(commands[1] in directory):
                                cli_sock.send("---+".encode('utf-8'))

                                # Collect all byted from file you are trying to transfer
                                f = open(commands[1],'rb')
                                print("Sending file to client")
                                data = f.read(33554432)
                                collection = data
                                while(data):
                                    print("Sending...")
                                    data = f.read(33554432)
                                    collection += data
                                print("")

                                # Encrypt the collected data using AES and send to client
                                fe = Fernet(key)
                                encrypted = fe.encrypt(collection)
                                cli_sock.sendall(encrypted)
                                f.close()
                                print("Finished sending file to client")
                                cli_sock.shutdown(socket.SHUT_WR)
                            
                            # Notify client that the file does not exist on the server and close connection
                            else:
                                cli_sock.send("----".encode('utf-8'))
                                time.sleep(1)
                                print("The server does not have the file client is attempting to download")
                                cli_sock.close()
                            
                        # Notify client that the provided password was incorrect
                        else:
                            cli_sock.send("----".encode('utf-8'))
                            print("Wrong client password provided")
                            time.sleep(1)
                            cli_sock.close()

                    # Handing of list request, server side
                    elif(commands[0] == "list"):
                        print("List request received")
                        directory = os.listdir()
                        directory_str = ""
                        
                        print("Sending list of File Directory...")

                        for file in directory:	
                            add = file + ", "		
                            directory_str += add

                        cli_sock.send(directory_str.encode('utf-8'))
                        print("Finished sending directory")
                        cli_sock.close()

                    else:
                        print("The connection encountered an error. Client must try again...")
                
                finally:
                    """
                    If an error occurs or the client closes the connection, call close() on the
                    connected socket to release the resources allocated to it by the OS.
                    """
                    print("The connection has been closed")
                    if 'cli_sock' in globals():
                        cli_sock.close()

            # Close the server socket as well to release its resources back to the OS
            srv_sock.close()
    else:
        print("Please enter a valid port number or password")
    
    if event in (None, 'Close Server'):   # if user closes window or clicks cancel
        break

    # Close the server socket as well to release its resources back to the OS
window.close()