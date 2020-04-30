import PySimpleGUI as sg
import socket
import sys
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

choices = ('put','get','list')
global key
global decrypted

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [  [sg.Text('Welcome to the privateshare client!', size=(30, 1), font=("Helvetica", 25), text_color='gray')],
            [sg.Text('Please enter the IP address of the Server:', size=(35, None)), sg.InputText()],
            [sg.Text('Please enter the Port Number of the Server:', size=(35, None)), sg.InputText()],
            [sg.Text('Please enter the Password of the Server:', size=(35, None)), sg.InputText()],
            [sg.Text('Filename you are tyring to download/upload:', size=(35, None)), sg.InputText()],
            [sg.Text('Server Operation: ', size=(35, None)), sg.Text('', size=(23, None)), sg.Combo(choices, size=(15, len(choices)), key='-CHOICE-')], 
            [sg.Output(size=(85,10), key='-OUTPUT-')],
            [sg.Text('')],
            [sg.Text('Transfer Progress: '),sg.ProgressBar(100, orientation='h', size=(38, 30), key='progressbar')],
            [sg.Text('')],
            [sg.Button('Connect'), sg.Button('Close Client')] ]

# Create the Window
window = sg.Window('privateshare client', layout)
progress_bar = window['progressbar']

# Event Loop to process "events" and get the "values" of the inputs
while True:
    # Create a client socket
    cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    event, values = window.read()
    if values[0] and values[1] and values['-CHOICE-']:
        server_ip = values[0]
        server_port = int(values[1])
        choice = str(values['-CHOICE-'])
        filename = str(values[3])
        password = str(values[2])
        # Prevent socket errors
        try:
            # Connect client socket to server socket
            cli_sock.connect((server_ip, server_port))
            srv_addr = (values[0], int(values[1]))

        except Exception as e:
            # Print the exception message
            print(e)
            print("")
    else:
        print("You are missing some input values. Please check you have entered all information correctly!")
    if event in (None, 'Close Client'):   # if user closes window or clicks cancel
        break

    try:
        while True:
            if choice:
                if(choice == 'put'):

                    # Make sure that the client directory contains the file it is trying to upload
                    directory = os.listdir()
                    if(not filename in directory):
                        print("You are trying to upload a file which does not exist. Please try again")
                        print("")
                        break
                    
                    else:
                        # Send the server the exact commands of the put request
                        cli_sock.send((choice + ',' + filename + ',' + password).encode('utf-8'))
                        checkuploadsallowed = cli_sock.recv(4)
                        if(checkuploadsallowed.decode('utf-8') == '----'):
                            print("Uploads are disabled for this server. Please contact the server maintainer or download a file")
                        elif(checkuploadsallowed.decode('utf-8') == '---+'):
                            checkpassword = cli_sock.recv(4)
                            if(checkpassword.decode('utf-8') == '----'):
                                print("Wrong password, please try again!")
                                break
                            elif(checkpassword.decode('utf-8') == '---+'):
                                key = cli_sock.recv(44)
                                print("Cryptographic Key has been successfully generated from the server.")
                                
                                # Before starting to send file, check that the server allows it. You cannot upload a file already on the server.
                                checkreupload = cli_sock.recv(4)

                                if(checkreupload.decode('utf-8') == '----'):
                                    print("You are trying to upload a file with a taken filename. Please alter the filename.")
                                    print("")
                                    break
                                
                                # If server allows it, continue to upload file to server.
                                elif(checkreupload.decode('utf-8') == '---+'):

                                    # Open the file you are trying to send
                                    f = open(filename,'rb')
                                    data = f.read(33554432)
                                    collection = data
                                    while(data):
                                        data = f.read(33554432)
                                        collection += data
                                        print("Sending file...")
                                        window.refresh()
                                    print("")

                                    # Encrypt the collected data using AES and send to client
                                    fe = Fernet(key)
                                    encrypted = fe.encrypt(collection)
                                    cli_sock.sendall(encrypted)
                                    f.close()
                                    print("Finished sending file to client")
                                    break

                elif(choice == 'get'):
                    # Make sure you don't have a file with the same filename already
                    directory = os.listdir()
                    if(not filename in directory):
                        cli_sock.send((choice + ',' + filename + ',' + password).encode('utf-8'))
                        checkpassword = cli_sock.recv(4)
                        
                        # Make sure the server password is correct
                        if(checkpassword.decode('utf-8') == '----'):
                            print("Wrong password, please try again!")
                            break
                        elif(checkpassword.decode('utf-8') == '---+'):
                            key = cli_sock.recv(44)
                            print("Key has been successfully generated from the server")
                            print("Waiting on server to encrypt file and send")
                            print("This might take a few moments and the program may appear frozen")
                            window.refresh()

                            checkreupload = cli_sock.recv(4)
                            # Check that the server has the file you are trying to download
                            if(checkreupload.decode('utf-8') == '----'):
                                print("You are trying to download a file that doesn't exist on the server. Please try again!")
                                print("")
                                break

                            # If the server has the file, continue to download file.
                            elif(checkreupload.decode('utf-8') == '---+'):
                                file_length = cli_sock.recv(16)
                                file_lengthy = file_length.decode('utf-8').split('**')
                                collection = file_lengthy[1].encode('utf-8')
                                f = open(str(filename),'wb')
                                data = cli_sock.recv(33554432)
                                window.refresh()
                                collection += data
                                while(data):
                                    data = cli_sock.recv(33554432)
                                    collection += data
                                    received = (int)(100*(len(collection)/int(file_lengthy[0])))
                                    print("Receiving..." + str(received) + "% complete")
                                    progress_bar.UpdateBar(received)
                                    window.refresh()
                                fe = Fernet(key)
                                print("Decrypting file...")
                                decrypted = fe.decrypt(collection)
                                f.write(decrypted)
                                f.close()
                                print("Done Receiving and Decrypting!!!")
                                print("")
                                break

                    else:
                        print("You already have a file with that filename in the directory you are trying to download into")
                        print("")
                        break

                elif(choice == 'list'):
                    print("Reqeusting File Directory from server...")
                    cli_sock.sendall(choice.encode('utf-8'))
                    directory = cli_sock.recv(33554432)
                    print("File Directory received:")
                    print(directory.decode('utf-8'))
                    print("")
                    break
            else:
                print("You need to select an operation")
    except Exception as e:
        # Print the exception message
        print(e)
        print("")
    finally:
        print("Client Socket has been closed")
        print("")
        cli_sock.close()

window.close()