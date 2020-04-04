import PySimpleGUI as sg
import socket
import sys
import os

choices = ('put','get','list')

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [  [sg.Text('Welcome to the privateshare client!')],
            [sg.Text('Please note that the Client will appear unresponsive during successful downloading/uploading')],
            [sg.Text('Please enter the IP address of the Server:'), sg.InputText()],
            [sg.Text('Please enter the Port Number of the Server:'), sg.InputText()],
            [sg.Listbox(choices, size=(15, len(choices)), key='-CHOICE-'), sg.Output(size=(50,10), key='-OUTPUT-')],
            [sg.Text('Filename you are tyring to download/upload:'), sg.InputText()],
            [sg.Button('Put/Get/List'), sg.Button('Close Client')] ]

# Create the Window
window = sg.Window('privateshare client', layout)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    # Create a client socket
    cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    event, values = window.read()
    server_ip = values[0]
    server_port = int(values[1])
    choice = str(values['-CHOICE-'][0])
    filename = str(values[2])
    if event in (None, 'Close Client'):   # if user closes window or clicks cancel
        break

    # Prevent errors
    try:
        # Connect client socket to server socket
        cli_sock.connect((server_ip, server_port))
        srv_addr = (values[0], int(values[1]))

    except Exception as e:
        # Print the exception message
        print(e)

    try:
        while True:
            if choice:
                if(choice == 'put'):
                    # Make sure that the client directory contains the file it is trying to upload
                    directory = os.listdir()
                    if(not filename in directory):
                        print("You are trying to upload a file which does not exist. Please try again")
                        break
                    else:
                        # Send the server the exact commands of the put request
                        cli_sock.sendall((choice + ',' + filename).encode('utf-8'))

                        # Open the file you are trying to send
                        f = open(filename,'rb')
                        data = f.read(33554432)

                        # Before starting to send file, check that the server allows it. You cannot upload a file already on the server.
                        checkreupload = cli_sock.recv(32)

                        if(checkreupload.decode('utf-8') == 'cancel'):
                            print("You are trying to upload a file with a taken filename. Please alter the filename.")
                            break

                        # If server allows it, continue to upload file to server.
                        if(checkreupload.decode('utf-8') == 'pass'):
                            while(data):
                                print("Uploading file to server...")
                                cli_sock.send(data)
                                data = f.read(33554432)
                            f.close()
                            print("Done uploading file to server!")
                            cli_sock.shutdown(socket.SHUT_WR)
                            break
                elif(choice == 'get'):
                    # Make sure you don't have a file with the same filename already
                    directory = os.listdir()
                    if(not filename in directory):

                    # Send the server the exact commands of the get request
                        cli_sock.send((choice + ',' + filename).encode('utf-8'))
                        checkreupload = cli_sock.recv(32)

                        # Check that the server has the file you are trying to download
                        if(checkreupload.decode('utf-8') == 'cancel'):
                            print("You are trying to download a file that doesn't exist on the server. Please try again!")
                            break

                        # If the server has the file, continue to download file.
                        if(checkreupload.decode('utf-8') == 'pass'):
                            f = open(str(filename),'wb')
                            data = cli_sock.recv(33554432)
                            while(data):
                                print("Receiving...")
                                f.write(data)
                                data = cli_sock.recv(33554432)
                            f.close()
                            print("Done Receiving")
                            break

                    else:
                        print("You already have a file with that filename in the directory you are trying to download into")
                        break

                elif(choice == 'list'):
                    print("Reqeusting File Directory from server...")
                    cli_sock.sendall(choice.encode('utf-8'))
                    directory = cli_sock.recv(33554432)
                    print("File Directory received:")
                    print(directory.decode('utf-8'))
                    break
            else:
                print("You need to select an operation")
    finally:
        cli_sock.close()
window.close()